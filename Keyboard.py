from tkinter import *

class KeyBoard:
    def __init__(self):
            self.root = Tk()
            self.root.title("Keyboard GUI")
            
            # Creating the input text
            self.text_var = StringVar()
            self.e = Entry(self.root, textvariable=self.text_var, width=50, font=('Helvetica', 16))
            self.e.grid(row=0, column=0, columnspan=11)
            self.cursorValue = 0  # Keeps track of the cursor position
            
            # Defining the buttons
            buttons = [
                ('Q', 1, 0), ('W', 1, 1), ('E', 1, 2), ('R', 1, 3), ('T', 1, 4), ('Y', 1, 5), ('U', 1, 6), ('I', 1, 7), ('O', 1, 8), ('P', 1, 9),
                ('A', 2, 0), ('S', 2, 1), ('D', 2, 2), ('F', 2, 3), ('G', 2, 4), ('H', 2, 5), ('J', 2, 6), ('K', 2, 7), ('L', 2, 8), ('Enter', 2, 9),
                ('Z', 3, 0), ('X', 3, 1), ('C', 3, 2), ('V', 3, 3), ('Space', 3, 4), ('B', 3, 6), ('N', 3, 7), ('M', 3, 8), (',', 3, 9), ('.', 3, 10)
            ]
            
            self.buttons = {}
            for (text, row, col) in buttons:
                self.buttons[text] = Button(self.root, text=text, padx=20, pady=20, command=lambda t=text: self.buttonClick(t), font=('Helvetica', 16))
                self.buttons[text].grid(row=row, column=col, sticky="ew" if text == "Space" else "")

            # Main Loop
            self.root.mainloop()
        
    def buttonClick(self, character):
        if character == "Enter":
            self.root.destroy()  # Close the GUI
        elif character == "Space":
            self.e.insert(self.cursorValue, " ")
            self.cursorValue += 1
        else:
            self.e.insert(self.cursorValue, character)
            self.cursorValue += 1
    
    def get_typed_text(self):
        return self.text_var.get()

    # Function to disable the buttons
    def disableRow1(self):
        for char in 'QWERTYUIOP':
            self.buttons[char].config(state=DISABLED, fg="black", bg="white")
        
    def disableRow2(self):
        for char in 'ASDFGHJKL':
            self.buttons[char].config(state=DISABLED, fg="black", bg="white")
        self.buttons["Enter"].config(state=DISABLED, fg="black", bg="white")
    
    def disableRow3(self):
        for char in 'ZXCVBNM,. ':
            self.buttons[char].config(state=DISABLED, fg="black", bg="white")
        self.buttons["Space"].config(state=DISABLED, fg="black", bg="white")
        
    # Function to Enable all the Rows
    def enableRow1(self):
        for char in 'QWERTYUIOP':
            self.buttons[char].config(state=NORMAL, fg="white", bg="black")
        
    def enableRow2(self):
        for char in 'ASDFGHJKL':
            self.buttons[char].config(state=NORMAL, fg="white", bg="black")
        self.buttons["Enter"].config(state=NORMAL, fg="white", bg="black")
    
    def enableRow3(self):
        for char in 'ZXCVBNM,. ':
            self.buttons[char].config(state=NORMAL, fg="white", bg="black")
        self.buttons["Space"].config(state=NORMAL, fg="white", bg="black")
    
    def start_timer(self):
        self.enableRow1()
        self.disableRow2()
        self.disableRow3()
        
        self.root.after(3000, self.switch_to_row2)  # Switch to Row 2 after 3 seconds
    
    def switch_to_row2(self):
        self.disableRow1()
        self.enableRow2()
        self.disableRow3()
        
        self.root.after(3000, self.switch_to_row3)  # Switch to Row 3 after 3 seconds
    
    def switch_to_row3(self):
        self.disableRow1()
        self.disableRow2()
        self.enableRow3()
        
        self.root.after(3000, self.start_timer)  # Switch back to Row 1 after 3 seconds
        
    def simulate_button_click(self, character):
        self.buttonClick(character)

# # Example usage
# k = KeyBoard()
# print(k.get_typed_text())
