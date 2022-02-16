import xml.etree.ElementTree as ET
import glob
import os
import zipfile
import babel.numbers
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import Calendar
from datetime import datetime, timedelta


class Interface:

    def __init__(self, frame):
        self.frame = Frame()
        self.create_calendar()
        self.create_input()
        self.create_buttons()
        self.output_path = filedialog.askdirectory(title = "Molimo izaberite početnu mapu") + '/'
        self.frame.pack()

    def create_calendar(self):
        self.cal = Calendar(self.frame, selectmode = 'day', date_pattern="yyyy-mm-dd")
        self.cal.grid(row=0 ,column=0, rowspan=4, padx=10, pady=10)
        
    def create_input(self):
        #Verzija
        self.num = Entry(self.frame, bd=2, justify='right')
        self.num.grid(row=0, column=1, pady=5, ipady=1, sticky=E, padx=20)
        Label(self.frame, text="Verzija").grid(row=0, column=2, sticky=W)

        #DayAhead/Intraday/Delete
        self.f310=IntVar()
        self.f710=IntVar()
        self.delete=IntVar()

        self.c1 = Checkbutton(self.frame, text="DayAhead", variable=self.f310)
        self.c2 = Checkbutton(self.frame, text="Intraday", variable=self.f710)
        self.d1 = Checkbutton(self.frame, text="Brisanje datoteka (2a_Input)", variable=self.delete)
        self.c1.grid(row=1, column=1)
        self.c2.grid(row=1, column=2)
        self.d1.grid(row=2, column=1, columnspan=2, sticky=E, padx=40)

    def create_buttons(self):
        b1 = Button(self.frame, text = "Zadržavanje FB domene", activebackground="#83868a", activeforeground="white", command=lambda : Methods.zadr_domene(self, self.output_path + '1a_Input_Zadrzavanje domene/original_file_1.xml', self.output_path + '1b_Output_Zadrzavanje domene/'))
        b2 = Button(self.frame, text = "Statistička validacija", activebackground="#83868a", activeforeground="white", command=lambda : Methods.stat_validacija(self))
        b3 = Button(self.frame, text = "Smanjenje za AMR na svim CNEC", activebackground="#83868a", activeforeground="white", command=lambda : Methods.smanjenjeAllCNEC(self)) 
        b4 = Button(self.frame, text = "Smanjenje za AMR na presolved CNEC", activebackground="#83868a", activeforeground="white", command=lambda : Methods.smanjenjePresolvedCNEC(self))

        b1.grid(row=3, column=1, columnspan=4, ipadx=50, ipady=10, padx=40)
        b2.grid(row=4, column=1, columnspan=4, ipadx=60, ipady=10)
        b3.grid(row=5, column=1, columnspan=4, ipadx=25, ipady=10, pady=10)
        b4.grid(row=6, column=1, columnspan=4, ipadx=12, ipady=10, pady=5)



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
            root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

            for identity in root.findall('{*}DocumentIdentification'):
                identity.set('v', '10XHR-HEP-OPS--A-' + self.date + '-'  + self.day + '-v' + self.version)
            
            for version in root.findall('{*}DocumentVersion'):
                version.set('v', self.version)

            for constraint in tree.findall('{*}ConstraintTimeInterval'):
                timeinterval = constraint.get('v')
                timeinterval = timeinterval.split('/')
                timeinterval1 = timeinterval[0].split('T')
                timeinterval2 = timeinterval[1].split('T')
                dateinterval = datetime.strptime(self.date_slash, '%Y-%m-%d')
                modified_date = dateinterval + timedelta(days=-1)
                modified_date = str(modified_date).split(' ')
                constraint.set('v',  str(modified_date[0]) + 'T'  + timeinterval1[1] + '/' + self.date_slash + 'T'+ timeinterval2[1])
            
            for creation in tree.findall('{*}CreationDateTime'):
                date_time = creation.get('v')
                date_time = date_time.split('T')
                creation.set('v', str(modified_date[0]) + 'T'  + date_time[1])

            
            tree.write(self.filename, encoding="utf-8", xml_declaration=True)
            
            messagebox.showinfo("Uspjeh!", "Datoteka: " + self.filename + "\n je uspješno stvorena u output mapi." + '\n\nZbog veličine, učitavanje podataka može potrajati nekoliko minuta.')

    def stat_validacija(self):
        
        input_folder = self.output_path + '2a_Input_Statisticka validacija/'
        output_folder = self.output_path + '2b_Output_Statisticka validacija/'
        
        file_list=[files for files in glob.glob1(input_folder, "*.xml")]

        Methods.zadr_domene(self, input_folder + file_list[0], output_folder)
        
        orig_tree = ET.parse(self.filename)
        root=orig_tree.getroot()
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        avs=orig_tree.find('{*}AdjustmentValues')

        #Spajanje xml dokumenata u jedan
        for i in range(1, len(file_list)):
            tree = ET.parse(input_folder + file_list[i])
            adj_value = tree.find('{*}AdjustmentValues')
            for values in adj_value.findall('{*}AdjustmentValue'):
                avs.append(values)
                                       
        #Mijenjanje <timeIntervala> u skladu sa odabranim vremenom
        dateinterval = datetime.strptime(self.date_slash, '%Y-%m-%d')
        for start in avs.findall('{*}AdjustmentValue'):
            for constraint in start.findall('{*}timeInterval'):
                modified_date = dateinterval + timedelta(days=-1)
                modified_date = str(modified_date).split(' ')
                timeinterval = constraint.get('v')
                timeinterval = timeinterval.split('/')
                timeinterval1 = timeinterval[0].split('T')
                timeinterval2 = timeinterval[1].split('T')
                if not timeinterval1[1].startswith('23'):
                    modified_date[0] = self.date_slash
                constraint.set('v', str(modified_date[0]) + 'T'  + timeinterval1[1] + '/' + self.date_slash  + 'T'+ timeinterval2[1])

        #Brisanje dupliciranih <AV> sa manjom vrijednoscu <IVA>
        for values in avs.findall('{*}AdjustmentValue'):
            for values_org in avs.findall('{*}AdjustmentValue'):
                if values_org.get('id') == values.get('id'):
                    if values_org.find('{*}timeInterval').get('v') == values.find('{*}timeInterval').get('v'):
                        if float(values_org.find('{*}IVA').text) < float(values.find('{*}IVA').text):
                            avs.remove(values_org)

        #Pregled preklapanja vremenskih intervala
        for values in avs.findall('{*}AdjustmentValue'):
            for values_org in avs.findall('{*}AdjustmentValue'):
                if values_org.get('id') == values.get('id'):
                    t1 = values_org.find('{*}timeInterval').get('v')
                    flst=[]
                    t2 = values.find('{*}timeInterval').get('v')
                    tlst=[]
                    
                    #prvi interval
                    h1 = list(t1[11]) + list(t1[12])
                    h1 = int(str(h1[0]) + str(h1[1]))
                    flst.append(h1)
                    h1 = timedelta(hours=h1)
                    
                    h2 = list(t1[29]) + list(t1[30])
                    h2 = int(str(h2[0]) + str(h2[1]))
                    flst.append(h2)
                    h2 = timedelta(hours=h2)
                    
                    #drugi interval
                    h1 = list(t2[11]) + list(t2[12])
                    h1 = int(str(h1[0]) + str(h1[1]))
                    tlst.append(h1)
                    h1 = timedelta(hours=h1)
                    
                    h2 = list(t2[29]) + list(t2[30])
                    h2 = int(str(h2[0]) + str(h2[1]))
                    tlst.append(h2)
                    h2 = timedelta(hours=h2)
                                        
                    if (tlst[0] <= flst[0] and flst[0] <= tlst[1]):
                        if (tlst[0] <= flst[1] and flst[1] <= tlst[1]):
                            if float(values_org.find('{*}IVA').text) < float(values.find('{*}IVA').text):
                                avs.remove(values_org)
                                a = values.find('{*}timeInterval')
                                a.set('v', t2)

                    if (flst[0] <= tlst[0] and tlst[0] <= flst[1]):
                        if (flst[0] <= tlst[1] and tlst[1] <= flst[1]):
                            if float(values_org.find('{*}IVA').text) < float(values.find('{*}IVA').text):
                                avs.remove(values_org)
                                a = values.find('{*}timeInterval')
                                a.set('v', t1)

        orig_tree.write(self.filename, encoding="utf-8", xml_declaration=True)

        #Brisanje datoteka u Input folderu
        if self.delete.get() == 1:
            for files in glob.glob1(input_folder, "*.xml"):
                os.remove(input_folder+files)


    def smanjenjeAllCNEC(self):
        
        input_folder = self.output_path + '1a_Input_Zadrzavanje domene/original_file_3-4.xml'
        output_folder = self.output_path + '3b_Output_Smanjenje za AMR na svim CNEC/'

        Methods.zadr_domene(self, input_folder, output_folder)

        orig_tree = ET.parse(self.filename)
        root=orig_tree.getroot()
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        avs = root.find('{*}AdjustmentValues')

        dir = self.output_path + '3a_Input_Smanjenje za AMR na svim CNEC/'
        for file in glob.glob1(dir, '*.zip'):
            with zipfile.ZipFile(dir + file, 'r') as zip_ref:
                zip_ref.extractall(dir)

        file_list=[files for files in glob.glob1(dir, "*.xml")]

        for i in range(0, len(file_list)):
            tree = ET.parse(dir + file_list[i])
            time = tree.find('{*}FlowBasedDomainTimeInterval').get('v')
            start = tree.find('.//{*}FlowBasedDomainTimeSeries/{*}Period/{*}Interval/{*}FlowBasedDomain/{*}constraintResults')
            for cr in start.findall('{*}constraintResult'):
                if cr.get('id').startswith('HR_'):
                    id = cr.get('id')
                    cb = cr.find('{*}criticalBranch')
                    name = cb.find('{*}monitoredBranch').get('name')
                    try:
                        amr = cb.find('{*}amr').text
                        cnec = cb.find('{*}CNEC').text
                        mnec = cb.find('{*}MNEC').text
                    except:
                        pass

                    if (int(amr)>0 and (cnec != 'false' or mnec != 'false')):
                        av = ET.SubElement(avs, 'AdjustmentValue')
                        av.set('name', name)
                        av.set('id', id)
                        ti = ET.SubElement(av, 'timeInterval')
                        ti.set('v', time)
                        iva = ET.SubElement(av, 'IVA')
                        iva.text = amr
                        jst = ET.SubElement(av, 'justification')
                        jst.text = 'IVA applied due to unsolvable overloads'
        

        dateinterval = datetime.strptime(self.date_slash, '%Y-%m-%d')
        for start in avs.findall('{*}AdjustmentValue'):
            for constraint in start.findall('{*}timeInterval'):
                modified_date = dateinterval + timedelta(days=-1)
                modified_date = str(modified_date).split(' ')
                timeinterval = constraint.get('v')
                timeinterval = timeinterval.split('/')
                timeinterval1 = timeinterval[0].split('T')
                timeinterval2 = timeinterval[1].split('T')
                if not timeinterval1[1].startswith('23'):
                    modified_date[0] = self.date_slash
                constraint.set('v', str(modified_date[0]) + 'T'  + timeinterval1[1] + '/' + self.date_slash  + 'T'+ timeinterval2[1])


        ET.indent(orig_tree, space=' ', level=0)
        orig_tree.write(self.filename, encoding="utf-8", xml_declaration=True)

        messagebox.showinfo("Uspjeh!", "Proces završio, rezultati su dostupni!")



    def smanjenjePresolvedCNEC(self):

        input_folder = self.output_path + '1a_Input_Zadrzavanje domene/original_file_3-4.xml'
        output_folder = self.output_path + '4b_Output_Smanjenje za AMR na presolved CNEC/'

        Methods.zadr_domene(self, input_folder, output_folder)

        orig_tree = ET.parse(self.filename)
        root=orig_tree.getroot()
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        avs = root.find('{*}AdjustmentValues')

        dir = self.output_path + '4a_Input_Smanjenje za AMR na presolved CNEC/'
        for file in glob.glob1(dir, '*.zip'):
            with zipfile.ZipFile(dir + file, 'r') as zip_ref:
                zip_ref.extractall(dir)

        file_list=[files for files in glob.glob1(dir, "*.xml")]
        for i in range(0, len(file_list)):
            tree = ET.parse(dir + file_list[i])
            time = tree.find('{*}FlowBasedDomainTimeInterval').get('v')
            start = tree.find('.//{*}FlowBasedDomainTimeSeries/{*}Period/{*}Interval/{*}FlowBasedDomain/{*}constraintResults')
            for cr in start.findall('{*}constraintResult'):
                if cr.get('id').startswith('HR_'):
                    rg = cr.find('.//{*}domainLimit/{*}region').text
                    tso = cr.find('.//{*}domainLimit/{*}tso').text
                    id = cr.get('id')
                    cb = cr.find('{*}criticalBranch')
                    name = cb.find('{*}monitoredBranch').get('name')
                    try:
                        amr = cb.find('{*}amr').text
                        cnec = cb.find('{*}CNEC').text
                        mnec = cb.find('{*}MNEC').text
                    except:
                        pass

                    if (int(amr)>0 and (cnec != 'false' or mnec != 'false') and (rg != 'false' or tso != 'false')):
                        av = ET.SubElement(avs, 'AdjustmentValue')
                        av.set('name', name)
                        av.set('id', id)
                        ti = ET.SubElement(av, 'timeInterval')
                        ti.set('v', time)
                        iva = ET.SubElement(av, 'IVA')
                        iva.text = amr
                        jst = ET.SubElement(av, 'justification')
                        jst.text = 'IVA applied due to unsolvable overloads'

        dateinterval = datetime.strptime(self.date_slash, '%Y-%m-%d')
        for start in avs.findall('{*}AdjustmentValue'):
            for constraint in start.findall('{*}timeInterval'):
                modified_date = dateinterval + timedelta(days=-1)
                modified_date = str(modified_date).split(' ')
                timeinterval = constraint.get('v')
                timeinterval = timeinterval.split('/')
                timeinterval1 = timeinterval[0].split('T')
                timeinterval2 = timeinterval[1].split('T')
                if not timeinterval1[1].startswith('23'):
                    modified_date[0] = self.date_slash
                constraint.set('v', str(modified_date[0]) + 'T'  + timeinterval1[1] + '/' + self.date_slash  + 'T'+ timeinterval2[1])

        ET.indent(orig_tree, space=' ', level=0)
        orig_tree.write(self.filename, encoding="utf-8", xml_declaration=True)

        messagebox.showinfo("Uspjeh!", "Proces završio, rezultati su dostupni!")


def main():
    canvas = Tk()
    canvas.geometry("600x400")
    canvas.title("Fallback FB CC Validation")
    canvas.iconbitmap('hops.ico')
    app = Interface(canvas)
    canvas.mainloop()


if __name__ == "__main__":
    main()
