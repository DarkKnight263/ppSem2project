import tkinter
import tkinter.messagebox
import socket
import customtkinter
from PIL import Image
import backend

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# storing frequently used colours as variables
fg1 = "#a01bf2"
hvr = "#3f1369"
fg2 = "#6a16b7"


# app and its widgets
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        fnt = customtkinter.CTkFont(family="HGGothicE", size=15)

        # dummy object
        self.backendObj = backend.backend("INR", -1, -1, -1, -1)
        self.backendObj.dbHandler()

        # configure window
        self.title("CRYTO-SPHERE")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        my_image = customtkinter.CTkImage(light_image=Image.open("cryptologo.png"), dark_image=Image.open("cryptologo.png"), size=(200, 200))

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="", font=customtkinter.CTkFont(size=20, weight="bold"), image=my_image)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.Currency_choice_label = customtkinter.CTkLabel(self.sidebar_frame, text="Currency ", anchor="w", font=fnt)
        self.Currency_choice_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.Currency_choice_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["INR(₹) ", "USD($)", "EUR(€)", "GBP(£)"], fg_color=fg1, button_color=fg2, button_hover_color=hvr, width=180, dropdown_hover_color=fg2)
        self.Currency_choice_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.Wifi_label = customtkinter.CTkLabel(self.sidebar_frame, text="Wi-Fi ", anchor="w", font=fnt)
        self.Wifi_label.grid(row=7, column=0, padx=20, pady=(10, 0))

        self.wifi_connect_label = customtkinter.CTkLabel(self.sidebar_frame, fg_color=fg1, width=180, corner_radius=8, text="Connected")
        self.wifi_connect_label.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.main_frame = customtkinter.CTkFrame(self, width=1000, height=600, fg_color="transparent", border_color=fg2, border_width=4)
        self.main_frame.grid(row=0, rowspan=10, column=1, padx=20, pady=(20, 0), sticky="nsew")

        # initialises and displays necessary widgets when device is offline
        if self.isConnect():
            self.plot_frame = customtkinter.CTkFrame(self.main_frame, width=960, height=50, fg_color="transparent", corner_radius=8)
            self.plot_frame.grid(row=0, column=0, padx=20, pady=(60, 20), sticky="ew")

            self.disp_label = customtkinter.CTkLabel(self.plot_frame, fg_color=hvr, font=fnt, text="Enter target price and tokens in front of respective crypto currency and click check", width=650, corner_radius=8)
            self.disp_label.pack(padx=(10, 5), pady=(10, 50), side="left")

            self.ref_button = customtkinter.CTkButton(self.plot_frame, fg_color=fg1, hover_color=hvr, font=fnt, text="CHECK", width=80, command=self.cmpr)
            self.ref_button.pack(padx=(5, 10), pady=(10, 50), side="left")

            self.plot_button = customtkinter.CTkButton(self.plot_frame, fg_color=fg1, hover_color=hvr, font=fnt, text="PLOT", width=180, command=self.plt)
            self.plot_button.pack(padx=10, pady=(10, 50), side="left")

            self.crypt1_frame = customtkinter.CTkFrame(self.main_frame, width=960, height=200, fg_color=fg2, corner_radius=8)
            self.crypt1_frame.grid(row=1, column=0, padx=20, pady=10)

            self.crypt1_cb = customtkinter.CTkCheckBox(self.crypt1_frame, corner_radius=8, fg_color=hvr, border_color=hvr, hover_color=hvr, border_width=2, width=180, height=180, font=fnt, text="DOGE")
            self.crypt1_cb.pack(padx=30, pady=10, side="left")

            self.crypt1_ent1 = customtkinter.CTkEntry(self.crypt1_frame, fg_color=hvr, border_color=hvr, border_width=2, width=330, height=100, font=fnt, placeholder_text="Target Price")
            self.crypt1_ent1.pack(side="left", padx=10, pady=50)
            self.crypt1_ent1.bind("<FocusOut>", lambda event: self.validate_float(self.crypt1_ent1))

            self.crypt1_ent2 = customtkinter.CTkEntry(self.crypt1_frame, fg_color=hvr, border_color=hvr, border_width=2, width=330, height=100, font=fnt, placeholder_text="Target Token Quantity")
            self.crypt1_ent2.pack(side="left", padx=(10, 20), pady=50)
            self.crypt1_ent2.bind("<FocusOut>", lambda event: self.validate_float(self.crypt1_ent2))

            self.crypt2_frame = customtkinter.CTkFrame(self.main_frame, width=960, height=200, fg_color=fg2, corner_radius=8)
            self.crypt2_frame.grid(row=2, column=0, padx=20, pady=10)

            self.crypt2_cb = customtkinter.CTkCheckBox(self.crypt2_frame, corner_radius=8, fg_color=hvr, border_color=hvr, hover_color=hvr, border_width=2, width=180, height=180, font=fnt, text="LTC")
            self.crypt2_cb.pack(padx=30, pady=10, side="left")

            self.crypt2_ent1 = customtkinter.CTkEntry(self.crypt2_frame, fg_color=hvr, border_color=hvr, border_width=2, width=330, height=100, font=fnt, placeholder_text="Target Price")
            self.crypt2_ent1.pack(side="left", padx=10, pady=50)
            self.crypt2_ent1.bind("<FocusOut>", lambda event: self.validate_float(self.crypt2_ent1))

            self.crypt2_ent2 = customtkinter.CTkEntry(self.crypt2_frame, fg_color=hvr, border_color=hvr, border_width=2, width=330, height=100, font=fnt, placeholder_text="Target Token Quantity")
            self.crypt2_ent2.pack(side="left", padx=(10, 20), pady=50)
            self.crypt2_ent2.bind("<FocusOut>", lambda event: self.validate_float(self.crypt2_ent2))

        # initialises and displays necessary widgets when device is offline
        else:
            self.off_label = customtkinter.CTkLabel(self.main_frame, text="Please connect to Wi-Fi and restart, press 'OK' to close the Application", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.off_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            self.re_button = customtkinter.CTkButton(self.main_frame, fg_color=fg1, hover_color=hvr, width=180, corner_radius=8, text="OK", command=self.restart_program)
            self.re_button.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

    # displays error message on a pop-up message box
    def error_box(self, txt):
        window = customtkinter.CTkToplevel(self)
        window.geometry("400x200+800+200")
        customtkinter.CTkLabel(window, font=("HGGothicE", 15), width=380, height=180, text=txt).pack(padx=10, pady=10)
        return 0

    # checks if wifi is connected
    def isConnect(self):
        try:
            s = socket.create_connection(("www.geeksforgeeks.org", 80))
            if s is not None:
                s.close()
                return True
        except OSError:
            self.wifi_connect_label.configure(text="NOT CONNECTED", fg_color="#FF0000")
            self.Currency_choice_optionemenu.configure(state="disabled")
            return False

    # destroys ap window
    def restart_program(self):
        self.destroy()

    # makes sure entryboxes can only store 2 decimal float values above zeros,rounds up or clears invalid values
    def validate_float(self, entry):
        try:
            value = float(entry.get())
            if value <= 0:
                entry.select_clear()
                entry.delete(0, "end")
                return False
            elif round(value, 2) == value:
                return True
            else:
                entry.select_clear()
                entry.delete(0, "end")
                entry.insert(0, round(value, 2))
                return False
        except ValueError:
            entry.select_clear()
            entry.delete(0, "end")
            return False

    # displays comparison values
    def cmpr_disp(self, cmprd):
        c1 = self.crypt1_cb.get()
        c2 = self.crypt2_cb.get()
        if c1 and c2:
            txt = "Target reached: DOGE: " + str(cmprd["DOGE"]) + " LTC: " + str(cmprd["LTC"])
        elif c1:
            txt = "Target reached: DOGE: " + str(cmprd["DOGE"])
        elif c2:
            txt = "Target reached: LTC: " + str(cmprd["LTC"])
        else:
            pass
        self.disp_label.configure(text=txt)

    # compares values entered in entry boxes with actual crypto rates,raises errors wherever necessary
    def cmpr(self):
        c1 = self.crypt1_cb.get()
        c2 = self.crypt2_cb.get()
        crypt1_box1 = 0
        crypt1_box2 = 0
        crypt2_box1 = 0
        crypt2_box2 = 0
        if c1 and c2:
            if len(self.crypt1_ent1.get()) > 0:
                crypt1_box1 = float(self.crypt1_ent1.get())
                if len(self.crypt1_ent2.get()) > 0:
                    crypt1_box2 = float(self.crypt1_ent2.get())
                    if len(self.crypt2_ent1.get()) > 0:
                        crypt2_box1 = float(self.crypt2_ent1.get())
                        if len(self.crypt2_ent2.get()) > 0:
                            crypt2_box2 = float(self.crypt2_ent2.get())
                        else:
                            self.error_box("PLEASE FILL NECESSARY FIELDS")
                    else:
                        self.error_box("PLEASE FILL NECESSARY FIELDS")
                else:
                    self.error_box("PLEASE FILL NECESSARY FIELDS")
            else:
                self.error_box("PLEASE FILL NECESSARY FIELDS")
        elif c1:
            if len(self.crypt1_ent1.get()) > 0:
                crypt1_box1 = float(self.crypt1_ent1.get())
                if len(self.crypt1_ent2.get()) > 0:
                    crypt1_box2 = float(self.crypt1_ent2.get())
                else:
                    self.error_box("PLEASE FILL NECESSARY FIELDS")
            else:
                self.error_box("PLEASE FILL NECESSARY FIELDS")
            crypt2_box1 = -1
            crypt2_box2 = -1
        elif c2:
            crypt1_box1 = -1
            crypt1_box2 = -1
            if len(self.crypt2_ent1.get()) > 0:
                crypt2_box1 = float(self.crypt2_ent1.get())
                if len(self.crypt2_ent2.get()) > 0:
                    crypt2_box2 = float(self.crypt2_ent2.get())
                else:
                    self.error_box("PLEASE FILL NECESSARY FIELDS")
            else:
                self.error_box("PLEASE FILL NECESSARY FIELDS")
        else:
            self.error_box("PLEASE SELECT ATLEAST ONE CRYPTO-CURRENCY")
        actual_backendObj = backend.backend(self.Currency_choice_optionemenu.get()[0:3], crypt1_box2, crypt1_box1, crypt2_box2, crypt2_box1)
        if(crypt1_box1 and crypt1_box2 and crypt2_box1 and crypt1_box2):
            self.cmpr_disp(actual_backendObj.compareTarget())

    # checks cryptos selected and plots them,raises errors wherever necessary
    def plt(self):
        c1 = self.crypt1_cb.get()
        c2 = self.crypt2_cb.get()
        if c1 and c2:
            self.backendObj.plot("DOGE")
            self.backendObj.plot("LTC")
        elif c1:
            self.backendObj.plot("DOGE")
        elif c2:
            self.backendObj.plot("LTC")
        else:
            self.error_box("PLEASE SELECT ATLEAST ONE CRYPTO-CURRENCY")


# main function that calls the app
if __name__ == "__main__":
    app = App()
    app.state("zoomed")
    app.mainloop()
