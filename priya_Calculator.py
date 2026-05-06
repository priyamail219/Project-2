import customtkinter as ctk
import math
import time

# UI Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DualSmartCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Priya's Ultimate Calculator")
        self.geometry("900x700") 
        self.resizable(False, False)

        self.expression = ""
        self.result_var = ctk.StringVar()
        self.mode = "DEG"
        
        self.setup_ui()
        self.bind("<Key>", self.keyboard_handler)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # LEFT: Calculator
        self.calc_frame = ctk.CTkFrame(self, corner_radius=0)
        self.calc_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.top_bar = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=(10, 0))
        
        self.mode_info = ctk.CTkLabel(self.top_bar, text="MODE: DEG", font=("Arial", 13, "bold"), text_color="#00f2fe")
        self.mode_info.pack(side="left")
        
        self.clock = ctk.CTkLabel(self.top_bar, text="", font=("Arial", 12), text_color="#aaaaaa")
        self.clock.pack(side="right")
        self.update_clock()

        self.screen = ctk.CTkEntry(self.calc_frame, textvariable=self.result_var, font=("Arial", 35, "bold"),
                                  height=100, corner_radius=15, fg_color="#1a1a1a",
                                  text_color="#ffffff", border_color="#333333", justify="right")
        self.screen.pack(pady=20, padx=20, fill="x")

        self.tab_view = ctk.CTkTabview(self.calc_frame, corner_radius=15)
        self.tab_view.pack(padx=15, pady=5, fill="both", expand=True)
        self.tab_std = self.tab_view.add("Standard")
        self.tab_sci = self.tab_view.add("Scientific")

        self.create_buttons()

        # RIGHT: History
        self.hist_frame = ctk.CTkFrame(self, width=280, corner_radius=10)
        self.hist_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.hist_frame, text="HISTORY", font=("Arial", 16, "bold"), text_color="#00adb5").pack(pady=10)
        
        self.history_box = ctk.CTkTextbox(self.hist_frame, font=("Arial", 13), fg_color="#1a1a1a", text_color="#00f2fe")
        self.history_box.pack(padx=10, pady=10, fill="both", expand=True)
        self.history_box.configure(state="disabled")

        ctk.CTkButton(self.hist_frame, text="Clear History", fg_color="#ff2e63", height=30, 
                      command=self.clear_history_box).pack(pady=10)

    def create_buttons(self):
        std_layout = [
            ['C', '⌫', '%', '÷'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '']
        ]
        sci_layout = [
            ['sin', 'cos', 'tan', '√'],
            ['log', 'ln', 'π', 'e'],
            ['x²', 'x³', 'x^y', 'fact'],
            ['(', ')', 'ABS', 'DEG'],
            ['RAD', 'EXP', 'C', '=']
        ]
        self.build_grid(self.tab_std, std_layout, 18)
        self.build_grid(self.tab_sci, sci_layout, 15)

    def build_grid(self, parent, layout, fsize):
        for r, row in enumerate(layout):
            for c, txt in enumerate(row):
                if txt == '': continue
                bg = "#2b2b2b"
                if txt == "=": bg = "#00adb5"
                elif txt in ['C', '⌫']: bg = "#ff2e63"
                
                btn = ctk.CTkButton(parent, text=txt, width=85, height=55, corner_radius=8,
                                   fg_color=bg, font=("Arial", fsize, "bold"),
                                   command=lambda x=txt: self.logic(x))
                btn.grid(row=r, column=c, padx=6, pady=6)

    def logic(self, btn):
        if btn == "=":
            self.solve()
        elif btn == "C":
            self.expression = ""
            self.result_var.set("")
        elif btn == "⌫":
            self.expression = self.expression[:-1]
            self.result_var.set(self.expression)
        elif btn in ["DEG", "RAD"]:
            self.mode = btn
            self.mode_info.configure(text=f"MODE: {btn}")
        elif btn == "x²": self.add_to_expr("**2")
        elif btn == "x³": self.add_to_expr("**3")
        elif btn == "x^y": self.add_to_expr("**")
        elif btn == "√": self.add_to_expr("sqrt(")
        elif btn == "π": self.add_to_expr("pi")
        elif btn == "e": self.add_to_expr("e")
        elif btn in ['sin', 'cos', 'tan', 'log', 'ln', 'fact']:
            self.add_to_expr(f"{btn}(")
        else:
            char = btn.replace("÷", "/")
            self.add_to_expr(char)

    def add_to_expr(self, val):
        self.expression += str(val)
        self.result_var.set(self.expression)

    def solve(self):
        if not self.expression: return
        
        try:
            # Trigonometry with Undefined 90 check
            def trig_check(func, x):
                if self.mode == "DEG":
                    angle = x % 360
                    if func == "tan" and (round(angle, 2) == 90.0 or round(angle, 2) == 270.0):
                        return "Undefined"
                    val = math.radians(x)
                else:
                    if func == "tan" and abs(math.cos(x)) < 1e-10:
                        return "Undefined"
                    val = x
                return getattr(math, func)(val)

            # Context for safe evaluation
            context = {
                "sin": lambda x: trig_check("sin", x),
                "cos": lambda x: trig_check("cos", x),
                "tan": lambda x: trig_check("tan", x),
                "log": lambda x: math.log10(x) if x > 0 else "Error",
                "ln": lambda x: math.log(x) if x > 0 else "Error",
                "sqrt": lambda x: math.sqrt(x) if x >= 0 else "Error",
                "fact": lambda x: math.factorial(int(x)) if x >= 0 else "Error",
                "pi": math.pi,
                "e": math.e,
                "abs": abs
            }

            # Solve
            res = eval(self.expression, {"__builtins__": None}, context)
            
            if res == "Undefined" or res == "Error":
                final_res = res
            else:
                final_res = round(res, 8) if isinstance(res, float) else res

            # Add to History
            self.update_history(f"{self.expression} = {final_res}")
            
            self.result_var.set(final_res)
            self.expression = str(final_res) if final_res not in ["Undefined", "Error"] else ""

        except ZeroDivisionError:
            self.result_var.set("Can't divide by 0")
            self.expression = ""
        except Exception:
            self.result_var.set("Format Error")
            self.expression = ""

    def update_history(self, text):
        self.history_box.configure(state="normal")
        self.history_box.insert("end", f"• {text}\n")
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

    def clear_history_box(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.configure(state="disabled")

    def keyboard_handler(self, event):
        k, s = event.char, event.keysym
        if s == "Return": self.solve()
        elif s == "BackSpace": self.logic("⌫")
        elif s == "Escape": self.logic("C")
        elif k in "0123456789.+-*/%()": self.logic(k.replace("/", "÷"))

    def update_clock(self):
        self.clock.configure(text=time.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = DualSmartCalculator()
    app.mainloop()