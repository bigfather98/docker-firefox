# mouse_controller.py
from flask import Flask, request, jsonify
import pyautogui
import time
import os

app = Flask(__name__)

pyautogui.FAILSAFE = False

@app.route('/mouse_action', methods=['GET', 'POST'])
def mouse_action():
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

        EXPECTED_TOKEN = os.environ.get("MOUSE_API_TOKEN", "token1") # Get token from ENV or default
        if not EXPECTED_TOKEN: # Ensure token is not empty
             print("Error: MOUSE_API_TOKEN is not set or is empty!")
             return jsonify({"status": "error", "message": "Server configuration error: API token missing"}), 500
        if secret_token != EXPECTED_TOKEN:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        if x is None or y is None:
            return jsonify({"status": "error", "message": "Missing 'x' or 'y' coordinates"}), 400

        x = int(x)
        y = int(y)

        screenWidth, screenHeight = pyautogui.size()
        if not (0 <= x < screenWidth and 0 <= y < screenHeight):
            return jsonify({
                "status": "error",
                "message": f"Coordinates ({x},{y}) are out of screen bounds ({screenWidth}x{screenHeight})"
            }), 400

        print(f"Mouse API: Received action: {action} at ({x},{y}), button: {button}, duration: {duration}")

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
            return jsonify({"status": "error", "message": "Invalid action specified"}), 400

        return jsonify({"status": "success", "message": message})

    except Exception as e:
        print(f"Mouse API Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    api_port = int(os.environ.get("MOUSE_API_PORT", 5001))
    print(f"Mouse Controller API starting on host 0.0.0.0 port {api_port}")
    app.run(host='0.0.0.0', port=api_port, debug=False)
