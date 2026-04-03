#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import re
import shutil
import time
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['LITELLM_LOG'] = 'ERROR'

class AIAgent:
    def __init__(self, root):
        self.root = root
        self.root.title("Dave - AI Agent")
        self.root.geometry("1000x850")
        self.root.configure(bg='#0f0f1a')
        self.is_processing = False
        self.conversation_history = []
        self.setup_ui()
        self.root.after(500, self.check_model_status)
    
    def check_model_status(self):
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            
            if 'deepseek-coder:1.3b' in result.stdout:
                self.update_status("Dave - Ready", '#4CAF50')
                self.update_output("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                self.update_output("Dave is ready to assist you\n")
                self.update_output("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                self.update_output("I can execute commands on your system\n")
                self.update_output("Tell me what you want me to do\n\n")
                self.update_output("Examples:\n")
                self.update_output("  • Create a file called hello.txt in Downloads\n")
                self.update_output("  • List all Python files in my Desktop\n")
                self.update_output("  • Write a Python script that prints hello world\n")
                self.update_output("  • Show me the current directory\n\n")
            else:
                self.update_status("Installing model...", '#ff9800')
                self.install_model()
                
        except Exception as e:
            self.update_status("Ollama not running", '#f44336')
            self.update_output("Ollama is not running\n\n")
            self.update_output("Please open a new terminal and run: ollama serve\n")
    
    def install_model(self):
        def install():
            self.update_output("Installing model...\n")
            self.update_output("This may take a few minutes\n\n")
            
            process = subprocess.Popen(
                ['ollama', 'pull', 'deepseek-coder:1.3b'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in process.stdout:
                self.update_output(line)
            
            process.wait()
            
            if process.returncode == 0:
                self.update_output("\nModel installed successfully\n")
                self.update_status("Dave - Ready", '#4CAF50')
            else:
                self.update_output("\nInstallation failed\n")
        
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    
    def setup_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg='#0f0f1a')
        main_container.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_container, bg='#0f0f1a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="DAVE", 
                              font=("Segoe UI", 28, "bold"), 
                              bg='#0f0f1a', 
                              fg='#ffffff')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="autonomous ai agent", 
                                 font=("Segoe UI", 10), 
                                 bg='#0f0f1a', 
                                 fg='#8888aa')
        subtitle_label.pack()
        
        # Separator line
        separator = tk.Frame(main_container, bg='#2a2a3a', height=1)
        separator.pack(fill='x', pady=(0, 20))
        
        # Input section
        input_frame = tk.Frame(main_container, bg='#0f0f1a')
        input_frame.pack(fill='x', pady=(0, 15))
        
        input_label = tk.Label(input_frame, text="command", 
                              bg='#0f0f1a', 
                              fg='#8888aa',
                              font=("Segoe UI", 10, "bold"))
        input_label.pack(anchor='w', pady=(0, 5))
        
        # Entry with modern styling
        self.entry = tk.Entry(input_frame, 
                             font=("Consolas", 11),
                             bg='#1a1a2a', 
                             fg='#ffffff',
                             insertbackground='#4CAF50',
                             relief='flat',
                             highlightthickness=1,
                             highlightcolor='#4CAF50',
                             highlightbackground='#2a2a3a')
        self.entry.pack(fill='x', pady=(0, 10), ipady=8)
        self.entry.bind('<Return>', lambda e: self.execute())
        
        # Button frame
        button_frame = tk.Frame(main_container, bg='#0f0f1a')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Modern button style function
        def create_button(parent, text, command, bg_color, hover_color):
            btn = tk.Button(parent, text=text, 
                          command=command,
                          bg=bg_color, 
                          fg='white',
                          font=("Segoe UI", 10, "bold"),
                          padx=20, 
                          pady=8,
                          relief='flat',
                          cursor='hand2',
                          borderwidth=0)
            btn.pack(side='left', padx=5)
            
            # Hover effect
            def on_enter(e):
                btn['background'] = hover_color
            def on_leave(e):
                btn['background'] = bg_color
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            return btn
        
        self.execute_btn = create_button(button_frame, "execute", self.execute, '#4CAF50', '#45a049')
        self.copy_btn = create_button(button_frame, "copy output", self.copy_output, '#2196F3', '#1976D2')
        self.clear_btn = create_button(button_frame, "clear all", self.clear_all, '#f44336', '#da190b')
        self.cancel_btn = create_button(button_frame, "cancel", self.cancel, '#ff9800', '#fb8c00')
        self.cancel_btn.config(state='disabled')
        
        # Status bar
        self.status = tk.Label(main_container, text="ready", 
                              bg='#0f0f1a', 
                              fg='#4CAF50',
                              font=("Segoe UI", 9),
                              anchor='w')
        self.status.pack(fill='x', pady=(0, 10))
        
        # Output section header
        output_header = tk.Frame(main_container, bg='#0f0f1a')
        output_header.pack(fill='x', pady=(10, 5))
        
        output_label = tk.Label(output_header, text="output", 
                               bg='#0f0f1a', 
                               fg='#8888aa',
                               font=("Segoe UI", 10, "bold"))
        output_label.pack(side='left')
        
        # Output text area with modern styling
        self.output = scrolledtext.ScrolledText(main_container, 
                                                height=24,
                                                bg='#1a1a2a', 
                                                fg='#e0e0e0',
                                                font=("Consolas", 10),
                                                wrap=tk.WORD,
                                                relief='flat',
                                                highlightthickness=1,
                                                highlightbackground='#2a2a3a',
                                                insertbackground='#4CAF50')
        self.output.pack(fill='both', expand=True, pady=(5, 10))
        
        # Progress bar (as label for now)
        self.progress = tk.Label(main_container, text="", 
                                bg='#0f0f1a', 
                                fg='#ff9800',
                                font=("Segoe UI", 9))
        self.progress.pack(fill='x', pady=(0, 5))
        
        self.create_context_menu()
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#2a2a3a', fg='white')
        self.context_menu.add_command(label="Copy", command=self.copy_output)
        self.context_menu.add_command(label="Copy All", command=self.copy_all_output)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.clear_output)
        self.output.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def copy_output(self):
        try:
            selected = self.output.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            self.update_status("copied", '#4CAF50')
            self.root.after(2000, lambda: self.update_status("ready", '#4CAF50'))
        except:
            all_text = self.output.get("1.0", tk.END)
            if all_text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(all_text)
                self.update_status("all copied", '#4CAF50')
                self.root.after(2000, lambda: self.update_status("ready", '#4CAF50'))
    
    def copy_all_output(self):
        all_text = self.output.get("1.0", tk.END)
        if all_text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
            self.update_status("all copied", '#4CAF50')
            self.root.after(2000, lambda: self.update_status("ready", '#4CAF50'))
    
    def clear_output(self):
        self.output.delete("1.0", tk.END)
    
    def update_status(self, text, color):
        try:
            self.status.config(text=text, fg=color)
            self.root.update()
        except:
            pass
    
    def update_output(self, text):
        try:
            self.output.insert(tk.END, text)
            self.output.see(tk.END)
            self.root.update()
        except:
            pass
    
    def update_progress(self, text):
        try:
            self.progress.config(text=text)
            self.root.update()
        except:
            pass
    
    def ask_ai_for_action(self, command):
        prompt = f"""You are Dave, an AI Agent that executes commands on a Linux system.

User command: "{command}"

You need to determine what action to take. Choose ONE of these:
1. FILE_OPERATION - If user wants to create, delete, move, or list files
2. CODE_GENERATION - If user wants to write code/scripts
3. SYSTEM_COMMAND - If user wants to run system commands
4. INFORMATION - If user wants information/explanation

Also provide the specific command to execute.

Respond in this format:
ACTION: <action_type>
COMMAND: <specific_command_to_execute>
EXPLANATION: <brief explanation>

Example responses:
- For "create file hello.txt in Downloads":
ACTION: FILE_OPERATION
COMMAND: touch ~/Downloads/hello.txt && echo "Created by Dave" > ~/Downloads/hello.txt
EXPLANATION: Creating file hello.txt in Downloads folder

- For "list all Python files":
ACTION: SYSTEM_COMMAND
COMMAND: find ~ -name "*.py" -type f 2>/dev/null | head -20
EXPLANATION: Listing Python files in home directory

Now respond for: {command}
"""
        
        result = subprocess.run(
            ['ollama', 'run', 'deepseek-coder:1.3b', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.stdout
    
    def parse_ai_response(self, response):
        action = "INFORMATION"
        command = ""
        explanation = ""
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('ACTION:'):
                action = line.replace('ACTION:', '').strip()
            elif line.startswith('COMMAND:'):
                command = line.replace('COMMAND:', '').strip()
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
        
        return action, command, explanation
    
    def execute_system_command(self, command):
        try:
            self.update_output(f"$ {command}\n\n")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                executable='/bin/bash'
            )
            
            output = ""
            for line in process.stdout:
                output += line
                self.update_output(line)
            
            process.wait()
            
            if process.returncode == 0:
                return f"\n[ exit code: 0 ]\n"
            else:
                error = process.stderr.read()
                return f"\n[ error: {error} ]\n"
                
        except Exception as e:
            return f"\n[ exception: {str(e)} ]\n"
    
    def execute(self):
        if self.is_processing:
            messagebox.showwarning("Busy", "Please wait for current task to complete")
            return
        
        command = self.entry.get().strip()
        
        if not command:
            messagebox.showwarning("Empty Command", "Please enter a command")
            return
        
        self.is_processing = True
        self.execute_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.update_status("processing", '#ff9800')
        self.update_progress("analyzing request...")
        
        self.update_output(f"\n{'-' * 70}\n")
        self.update_output(f"[user] {command}\n")
        self.update_output(f"{'-' * 70}\n\n")
        thread = threading.Thread(target=self.process_command, args=(command,))
        thread.daemon = True
        thread.start()
    
    def process_command(self, command):
        try:
            self.update_output("[dave] analyzing...\n")
            ai_response = self.ask_ai_for_action(command)
            action, cmd_to_execute, explanation = self.parse_ai_response(ai_response)
            
            self.update_output(f"[dave] action: {action}\n")
            if explanation:
                self.update_output(f"[dave] plan: {explanation}\n")
            self.update_output(f"\n")
            
            if action in ["FILE_OPERATION", "SYSTEM_COMMAND", "CODE_GENERATION"] and cmd_to_execute:
                self.update_output(f"[executing] {cmd_to_execute}\n\n")
                result = self.execute_system_command(cmd_to_execute)
                self.update_output(result)
                
            elif action == "INFORMATION":
                self.update_output("[dave] retrieving information...\n\n")
                answer = subprocess.run(
                    ['ollama', 'run', 'deepseek-coder:1.3b', command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                self.update_output(answer.stdout)
                self.update_output("\n")
            else:
                self.update_output("[dave] unable to determine action\n")
                self.update_output(f"response: {ai_response}\n")
            
            self.update_output(f"\n{'-' * 70}\n")
            self.update_output("[dave] task completed\n\n")
            
            self.update_status("ready", '#4CAF50')
            self.update_progress("")
            
        except Exception as e:
            self.update_output(f"\n[error] {str(e)}\n")
            self.update_status("error", '#f44336')
            self.update_progress("")
        
        finally:
            self.is_processing = False
            self.execute_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
    
    def cancel(self):
        self.is_processing = False
        self.update_status("cancelled", '#ff9800')
        self.update_progress("")
        self.update_output("\n[operation cancelled]\n\n")
        self.execute_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
    
    def clear_all(self):
        self.entry.delete(0, tk.END)
        self.output.delete("1.0", tk.END)
        self.update_status("ready", '#4CAF50')
        self.update_progress("")
        self.update_output("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.update_output("Dave is ready\n")
        self.update_output("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
        self.update_output("Tell me what you want me to do\n")
        self.update_output("I can create files, run commands, write code, and more\n\n")
        self.update_output("Try these:\n")
        self.update_output("  • Create a file called test.txt in Downloads\n")
        self.update_output("  • List all files in my Desktop\n")
        self.update_output("  • Write a Python script that prints hello\n")
        self.update_output("  • What is the current date and time?\n\n")

def on_closing():
    if messagebox.askokcancel("Quit", "Exit Dave?"):
        root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    app = AIAgent(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
        
