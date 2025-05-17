# mouse_controller.py
print("MOUSE_CONTROLLER.PY: Script execution started.", flush=True)

try:
    print("MOUSE_CONTROLLER.PY: Importing Flask...", flush=True)
    from flask import Flask, request, jsonify
    print("MOUSE_CONTROLLER.PY: Flask imported.", flush=True)

    print("MOUSE_CONTROLLER.PY: Importing pyautogui...", flush=True)
    import pyautogui
    print("MOUSE_CONTROLLER.PY: pyautogui imported.", flush=True)

    print("MOUSE_CONTROLLER.PY: Importing time...", flush=True)
    import time
    print("MOUSE_CONTROLLER.PY: time imported.", flush=True)

    print("MOUSE_CONTROLLER.PY: Importing os...", flush=True)
    import os
    print("MOUSE_CONTROLLER.PY: os imported.", flush=True)

    print("MOUSE_CONTROLLER.PY: All imports successful. Defining Flask app.", flush=True)
    app = Flask(__name__)

    print("MOUSE_CONTROLLER.PY: Setting pyautogui.FAILSAFE.", flush=True)
    pyautogui.FAILSAFE = False
    print("MOUSE_CONTROLLER.PY: pyautogui.FAILSAFE set.", flush=True)

    @app.route('/mouse_action', methods=['GET', 'POST'])
    def mouse_action():
        # print("MOUSE_CONTROLLER.PY: /mouse_action endpoint hit.", flush=True) # Optional: uncomment for request logging
        try:
            if request.method == 'POST':
                data = request.get_json()
            else: # GET request
                data = request.args

            x = data.get('x')
            y = data.get('y')
            action = data.get('action', 'move_click')
            button = data.get('button', 'left')
            duration = float(data.get('duration', 0.2))
            secret_token = data.get('token')

            EXPECTED_TOKEN = os.environ.get("MOUSE_API_TOKEN", "your_super_secret_token_123")
            if not EXPECTED_TOKEN:
                 print("MOUSE_CONTROLLER.PY: Error: MOUSE_API_TOKEN is not set or is empty!", flush=True)
                 return jsonify({"status": "error", "message": "Server configuration error: API token missing"}), 500
            if secret_token != EXPECTED_TOKEN:
                print(f"MOUSE_CONTROLLER.PY: Unauthorized attempt. Received token: '{secret_token}'", flush=True)
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            if x is None or y is None:
                print(f"MOUSE_CONTROLLER.PY: Missing coordinates. Data: {data}", flush=True)
                return jsonify({"status": "error", "message": "Missing 'x' or 'y' coordinates"}), 400

            x = int(x)
            y = int(y)

            # print("MOUSE_CONTROLLER.PY: Getting screen size...", flush=True) # Optional
            screenWidth, screenHeight = pyautogui.size()
            if not (0 <= x < screenWidth and 0 <= y < screenHeight):
                print(f"MOUSE_CONTROLLER.PY: Coords out of bounds. ({x},{y}) vs ({screenWidth}x{screenHeight})", flush=True)
                return jsonify({
                    "status": "error",
                    "message": f"Coordinates ({x},{y}) are out of screen bounds ({screenWidth}x{screenHeight})"
                }), 400

            print(f"MOUSE_CONTROLLER.PY: Mouse API: Received action: {action} at ({x},{y}), button: {button}, duration: {duration}", flush=True)

            message = ""
            if action == 'move':
                pyautogui.moveTo(x, y, duration=duration)
                message = f"Mouse moved to ({x},{y})"
            elif action == 'click':
                pyautogui.moveTo(x, y, duration=duration)
                pyautogui.click(button=button)
                message = f"Mouse clicked {button} button at ({x},{y})"
            elif action == 'move_click':
                pyautogui.moveTo(x, y, duration=duration)
                time.sleep(0.1)
                pyautogui.click(button=button)
                message = f"Mouse moved to ({x},{y}) and clicked {button} button"
            elif action == 'double_click':
                pyautogui.moveTo(x, y, duration=duration)
                time.sleep(0.1)
                pyautogui.doubleClick(button=button)
                message = f"Mouse double-clicked {button} button at ({x},{y})"
            elif action == 'right_click':
                pyautogui.moveTo(x, y, duration=duration)
                time.sleep(0.1)
                pyautogui.rightClick()
                message = f"Mouse right-clicked at ({x},{y})"
            else:
                print(f"MOUSE_CONTROLLER.PY: Invalid action: {action}", flush=True)
                return jsonify({"status": "error", "message": "Invalid action specified"}), 400

            # print(f"MOUSE_CONTROLLER.PY: Action '{action}' successful. Message: {message}", flush=True) # Optional
            return jsonify({"status": "success", "message": message})

        except Exception as e_route:
            print(f"MOUSE_CONTROLLER.PY: ERROR IN /mouse_action endpoint: {e_route}", flush=True)
            return jsonify({"status": "error", "message": str(e_route)}), 500

    if __name__ == '__main__':
        print("MOUSE_CONTROLLER.PY: Inside __main__ block.", flush=True)
        api_port = int(os.environ.get("MOUSE_API_PORT", 5001))
        # This is the original line we are looking for
        print(f"Mouse Controller API starting on host 0.0.0.0 port {api_port}", flush=True)
        try:
            # Consider debug=True temporarily if Flask itself might be erroring silently
            # However, debug=True can be problematic for s6 if it tries to reload on code changes.
            app.run(host='0.0.0.0', port=api_port, debug=False)
            # This line should ideally not be reached if app.run() blocks as expected
            print("MOUSE_CONTROLLER.PY: app.run() finished (unexpected for a daemon).", flush=True)
        except Exception as e_run:
            print(f"MOUSE_CONTROLLER.PY: CRITICAL ERROR IN APP.RUN(): {e_run}", flush=True)
            # import sys
            # sys.exit(1) # Force non-zero exit if app.run fails

except ImportError as e_import:
    print(f"MOUSE_CONTROLLER.PY: CRITICAL IMPORT ERROR: {e_import}", flush=True)
    # import sys
    # sys.exit(1) # Exit to make s6 aware of failure
except Exception as e_global:
    print(f"MOUSE_CONTROLLER.PY: CRITICAL GLOBAL ERROR (before app.run or imports): {e_global}", flush=True)
    # import sys
    # sys.exit(1)

print("MOUSE_CONTROLLER.PY: Script execution reached very end (this is bad if app.run was expected to block).", flush=True)
