import tkinter as tk

from Gui_Chores import Chore
from Gui_EnvyFreeness import CakeUI

class FairDivisionHub:
    def __init__(self, root):
        self.root = root
        self.root.title("Fair Division Hub")
        self.root.geometry("800x550")
        self.root.configure(background="#1e293b")
        self.root.resizable(False, False)

        self.active_cake = None
        self.active_chore = None

        self.setup_dashboard_ui()

    def setup_dashboard_ui(self):
        hub_frame = tk.Frame(self.root, bg="#0f172a", pady=30)
        hub_frame.pack(fill="x")

        tk.Label(hub_frame, text="Fair Division Hub", font=("Helvetica", 16, "bold"), fg="#f8fafc", bg="#0f172a").pack()

        card_container = tk.Frame(self.root, bg="#1e293b", pady=30)
        card_container.pack(fill="both", expand=True)

        #Cake division

        card_cake = tk.LabelFrame(card_container, text="Envy-Freeness Cake Cutting", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#6a53ac", padx=15, pady=15, bd=1, relief="solid", width=340, height=260)
        card_cake.pack(side="left", padx=30, fill="both", expand=True)
        card_cake.pack_propagate(False)

        lbl_cake_description = tk.Label(card_cake,
                                        text="Handles assets/goods division through Cut-and-Choose, Selfridge-Conway, Even-Paz to make it so Players dont feel envy.",
                                        font=("Helvetica", 8), fg="#6a53ac", bg="#ffffff", justify="left", wrap=290)
        lbl_cake_description.pack(anchor="nw", fill="x", expand=True)

        btn_launch_cake = tk.Button(card_cake, text="Launch Cake Cutting", command=self.launch_cake_cutting, fg="#ffffff", bg="#6a53ac", font=("Helvetica", 10, "bold"), bd=0, cursor="hand2", pady=8)
        btn_launch_cake.pack(side="bottom", fill="x")

        #Chore division

        card_chore = tk.LabelFrame(card_container, text="Envy-Freeness Chore Division", font=("Helvetica", 10, "bold"),
                                  bg="#ffffff", fg="#a4745b", padx=15, pady=15, bd=1, relief="solid", width=340,
                                  height=260)
        card_chore.pack(side="right", padx=30, fill="both", expand=True)
        card_chore.pack_propagate(False)

        lbl_chore_description = tk.Label(card_chore,
                                        text="divides tasks between players so all have an equal amount of disutility. Links tasks that have the same ID and give them to one person. Players and Tasks also have types, with these Players can only get tasks of the same type unless they are marked with the any type.\nPlayers can  export the table of the division, as well as a calendar",
                                        font=("Helvetica", 8), fg="#a4745b", bg="#ffffff", justify="left", wrap=290)
        lbl_chore_description.pack(anchor="nw", fill="x", expand=True)

        btn_launch_chore = tk.Button(card_chore, text="Launch Chore Division", command=self.launch_chore_division,
                                    fg="#ffffff", bg="#a4745b", font=("Helvetica", 10, "bold"), bd=0, cursor="hand2",
                                    pady=8)
        btn_launch_chore.pack(side="bottom", fill="x")

    def launch_cake_cutting(self):
        if self.active_cake is not None and tk.Toplevel.winfo_exists(self.active_cake):
            self.active_cake.lift()
            return
        self.active_cake = tk.Toplevel(self.root)

        CakeUI(self.active_cake)


    def launch_chore_division(self):
        if self.active_chore is not None and tk.Toplevel.winfo_exists(self.active_chore):
            self.active_chore.lift()
            return
        self.active_chore = tk.Toplevel(self.root)

        Chore(self.active_chore)

if __name__ == "__main__":
    root = tk.Tk()
    hub = FairDivisionHub(root)
    root.mainloop()
