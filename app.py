from flask import Flask, request, jsonify
import tempfile
import subprocess
import json
import os
import uuid
import logging
import sys

# Configure logging to show on stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute():
    try:
        logger.info("Received new execution request")
        data = request.get_json()
        logger.info("Request data: %s", data)

        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in request body"}), 400

        script_content = data['script']
        logger.info("Script content: %s", script_content)

        if 'def main()' not in script_content:
            return jsonify({"error": "Script must define a main() function"}), 400

        # Create a unique filename for the script
        script_filename = f"/tmp/{uuid.uuid4().hex}.py"
        result_json_path = f"/tmp/{os.path.basename(script_filename)}.out.json"
        
        # Wrap the script with code to write the result to a file
        wrapped_script = f"""
import json
import sys
print("Starting script execution", file=sys.stderr)
{script_content}

if __name__ == "__main__":
    try:
        print("Calling main()", file=sys.stderr)
        result = main()
        print(f"Main returned: {{result}}", file=sys.stderr)
        with open("{result_json_path}", "w") as f:
            json.dump(result, f)
        print("Result written to file", file=sys.stderr)
    except Exception as e:
        print(f"Error occurred: {{str(e)}}", file=sys.stderr)
        with open("{result_json_path}", "w") as f:
            json.dump({{"error": str(e)}}, f)
"""
        
        logger.info("Writing script to file: %s", script_filename)
        with open(script_filename, "w") as f:
            f.write(wrapped_script)

        logger.info("Executing script with nsjail")
        # Run the script inside nsjail with minimal settings
        cmd = [
            "nsjail",
            "--quiet",
            "--mode", "o",  # STANDALONE mode
            "--disable_clone_newnet",
            "--disable_clone_newuser",
            "--disable_clone_newns",
            "--disable_clone_newpid",
            "--disable_clone_newipc",
            "--disable_clone_newuts",
            "--disable_clone_newcgroup",
            "--disable_proc",
            "--disable_rlimits",
            "--time_limit", "5",
            "--",
            sys.executable,
            script_filename
        ]
        logger.info("Running command: %s", " ".join(cmd))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        logger.info("Script execution completed with return code: %d", result.returncode)
        logger.info("stdout: %s", result.stdout)
        logger.info("stderr: %s", result.stderr)

        # Check if execution failed
        if result.returncode != 0:
            return jsonify({
                "error": "Script execution failed",
                "stdout": result.stdout,
                "stderr": result.stderr
            }), 500

        # Try to extract the return value
        if not os.path.exists(result_json_path):
            logger.error("Result file not found: %s", result_json_path)
            return jsonify({"error": "main() must return a JSON-serializable value"}), 500

        with open(result_json_path, "r") as f:
            output = json.load(f)

        if "error" in output:
            return jsonify({"error": output["error"]}), 500

        return jsonify({"result": output, "stdout": result.stdout})

    except subprocess.TimeoutExpired:
        logger.error("Script execution timed out")
        return jsonify({"error": "Script execution timed out"}), 408
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", str(e))
        return jsonify({"error": "main() must return a JSON-serializable value"}), 500
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        try:
            if os.path.exists(script_filename):
                os.remove(script_filename)
            if os.path.exists(result_json_path):
                os.remove(result_json_path)
        except Exception as e:
            logger.error("Error cleaning up files: %s", str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
