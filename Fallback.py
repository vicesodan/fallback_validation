import xml.etree.ElementTree as ET
import glob
from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta


class Interface:

    def __init__(self, frame):
        self.frame = Frame()
        self.create_calendar()
        self.create_input()
        self.create_buttons()
        self.frame.pack()

    def create_calendar(self):
        self.cal = Calendar(self.frame, selectmode = 'day', date_pattern="yyyy-mm-dd")
        self.cal.grid(row=0 ,column=0, rowspan=4, padx=10, pady=10)
        

    def create_input(self):
        #Verzija
        self.num = Entry(self.frame, bd=2, justify='right')
        self.num.grid(row=0, column=1, pady=5, ipady=1, sticky=E, padx=20)
        Label(self.frame, text="Verzija").grid(row=0, column=2, sticky=W)

        #DayAhead/Intraday
        self.f310=IntVar()
        self.f710=IntVar()

        self.c1 = Checkbutton(self.frame, text="DayAhead", variable=self.f310)
        self.c2 = Checkbutton(self.frame, text="Intraday", variable=self.f710)
        self.c1.grid(row=1, column=1)
        self.c2.grid(row=1, column=2)

    def create_buttons(self):
        b1 = Button(self.frame, text = "Zadržavanje FB domene", activebackground="#83868a", activeforeground="white", command=lambda : Methods.zadr_domene(self, '20211217-F310-v1-10XHR-HEP-OPS--A-to-17XTSO-CS------W.xml', 'C:/Users/vsodan2/Desktop/INPUTS_OUTPUTS/1b_Output_Zadrzavanje domene/'))
        b2 = Button(self.frame, text = "Statističkva validacija", activebackground="#83868a", activeforeground="white", command=lambda : Methods.stat_validacija(self))
        b3 = Button(self.frame, text = "Smanjenje za AMR na svim CNEC", state = "disabled")
        b4 = Button(self.frame, text = "Smanjenje za AMR na presolved CNEC", state = "disabled")

        b1.grid(row=2, column=1, columnspan=4, ipadx=50, ipady=10, padx=40)
        b2.grid(row=3, column=1, columnspan=4, ipadx=57.5, ipady=10)
        b3.grid(row=4, column=1, columnspan=4, ipadx=25, ipady=10, pady=10)
        b4.grid(row=5, column=1, columnspan=4, ipadx=12, ipady=10, pady=5)



class Methods(Interface):
    
    def zadr_domene(self, orig_file, dest_folder):
        check=1
        try:
            int(self.num.get())
        except ValueError:
            messagebox.showerror("Pogrešan unos", "Molimo unesite broj u polje za verziju.")
            check=0

        if ((self.f310.get() == 1 and self.f710.get() == 1) or (self.f310.get() == 0 and self.f710.get() == 0)):
            messagebox.showerror("Pogrešan unos", "Molimo odaberite DayAhead ILI Intraday.")
            check=0

        if (check==1):
            self.version = self.num.get()
            self.date_slash =  self.cal.get_date()
            self.date = self.date_slash.split('-')
            self.date = ''.join(self.date)
            if (self.f310.get() == 1):
                self.day = "F310"
            elif (self.f710.get() == 1):
                self.day = "F710"

            self.filename = dest_folder + self.date + '-' + self.day + '-v' + self.version + '-10XHR-HEP-OPS--A-to-17XTSO-CS------W.xml'

            tree = ET.parse(orig_file)
            root = tree.getroot()
            ET.register_namespace("","flowbased")

            for identity in root.findall('{*}DocumentIdentification'):
                identity.set('v', '10XHR-HEP-OPS--A-' + self.date + '-'  + self.day + '-v' + self.version)

            for creation in tree.findall('{*}CreationDateTime'):
                date_time = creation.get('v')
                date_time = date_time.split('T')
                creation.set('v', self.date_slash + 'T'  + date_time[1])

            for constraint in tree.findall('{*}ConstraintTimeInterval'):
                timeinterval = constraint.get('v')
                timeinterval = timeinterval.split('/')
                timeinterval1 = timeinterval[0].split('T')
                timeinterval2 = timeinterval[1].split('T')
                dateinterval = datetime.strptime(self.date_slash, '%Y-%m-%d')
                modified_date = dateinterval + timedelta(days=1)
                modified_date = str(modified_date).split(' ')
                constraint.set('v', self.date_slash + 'T'  + timeinterval1[1] + '/' + str(modified_date[0]) + 'T'+ timeinterval2[1])

            
            tree.write(self.filename)
            
            messagebox.showinfo("Uspjeh!", "Datoteka: " + self.filename + "\n je uspješno stvorena u output mapi." + self.date_slash)

    def stat_validacija(self):
        
        input_folder = 'C:/Users/vsodan2/Desktop/INPUTS_OUTPUTS/2a_Input_Statisticka validacija/'
        output_folder = 'C:/Users/vsodan2/Desktop/INPUTS_OUTPUTS/2b_Output_Statisticka validacija/'
        file_list=[]

        for files in glob.glob1(input_folder, "*.xml"):
            file_list.append(files)

        Methods.zadr_domene(self, input_folder + file_list[0], output_folder)
        
        orig_tree = ET.parse(input_folder + file_list[0])
        av=orig_tree.find('{*}AdjustmentValues')

        for i in range(1, len(file_list)):
            tree = ET.parse(input_folder + file_list[i])
            root=tree.getroot()
            adj_value = tree.find('{*}AdjustmentValues')
            for values in adj_value.findall('{*}AdjustmentValue'):
                av.append(values)

        orig_tree.write(self.filename)


def main():
    canvas = Tk()
    canvas.geometry("600x400")
    canvas.title("Fallback FB CC Validation")
    canvas.iconbitmap('hops.ico')
    app = Interface(canvas)
    canvas.mainloop()


if __name__ == "__main__":
    main()