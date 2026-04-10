import time
import subprocess
import psutil
import os

def find_processes():
    train_proc = None
    app_proc = None
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = p.info.get('cmdline')
            if not cmd:
                continue
            cmdline = " ".join(cmd).lower()
            if 'python' in p.info.get('name', '').lower() and 'train_model.py' in cmdline:
                train_proc = p
            elif 'python' in p.info.get('name', '').lower() and 'app.py' in cmdline:
                app_proc = p
        except Exception:
            pass
    return train_proc, app_proc

if __name__ == "__main__":
    train_p, app_p = find_processes()
    
    if train_p:
        print(f"Waiting for train_model.py (PID {train_p.pid}) to finish training...")
        try:
            train_p.wait()
        except psutil.TimeoutExpired:
            pass
    
    print("Training process has completed!")
    
    # Refresh to find app.py again just in case PID changed
    _, current_app_p = find_processes()
    if current_app_p:
        print(f"Terminating old app.py (PID {current_app_p.pid})...")
        try:
            current_app_p.terminate()
            current_app_p.wait(timeout=5)
        except Exception as e:
            print(f"Force killing app.py... {e}")
            try:
                current_app_p.kill()
            except:
                pass
                
    print("Launching new app.py server with updated AI weights...")
    app_script = os.path.join(os.path.dirname(__file__), 'backend', 'app.py')
    subprocess.Popen(["python", app_script])
    print("Watcher executed successfully. The web app is now running with the newly trained model!")
