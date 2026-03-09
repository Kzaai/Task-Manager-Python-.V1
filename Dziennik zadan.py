import os 
import customtkinter as ctk
import json
from datetime import datetime 



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCIEZKA_PLIKU = os.path.join(BASE_DIR, "dziennik_zadan.txt")
#Ustawiam Styl
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class DziennikZadan(ctk.CTk):
    def __init__(self):
        super().__init__()
        
           
        
        # 1. Konfiguracja okna
        self.title("Task Manager")
        self.geometry("900x700")

        # 2. Zakładki
        self.tabview = ctk.CTkTabview(self, width=650, height=550)
        self.tabview.pack(pady=10)
        self.tabview.add("Warsztat")
        self.tabview.add("Twoja Lista")
        self.tabview.add("Inne")


        #---- Zakładka: Inne -----

        self.listbox = ctk.CTkTextbox(self.tabview.tab("Inne"), width=600, height=350, font=("Arial", 16), state ="disabled")
        self.listbox.pack(pady=10)

        # --- ZAKŁADKA: WARSZTAT ---
        self.entry = ctk.CTkEntry(self.tabview.tab("Warsztat"), placeholder_text="Wpisz zadanie....", width=400)
        self.entry.pack(pady=30)

        self.button_add = ctk.CTkButton(self.tabview.tab("Warsztat"), text="DODAJ ZADANIE!!", command=self.dodaj_zadanie, cursor="hand2")
        self.button_add.pack(pady=10)

        # --- ZAKŁADKA: TWOJA LISTA ---

        #Kolumny 

        self.tabview.tab("Twoja Lista").grid_columnconfigure(0, weight=3)
        self.tabview.tab("Twoja Lista").grid_columnconfigure(1, weight=1)

        #Główne Okno z zadaniami 
        
        self.textbox = ctk.CTkTextbox(self.tabview.tab("Twoja Lista"), width=600, height=350, font=("Arial", 16), state ="disabled")
        self.textbox.grid(row=0, column = 10, rowspan= 6, padx=10, pady=10, sticky= "nsew")

        self.button_finish = ctk.CTkButton(self.tabview.tab("Twoja Lista"), text="ZAKOŃCZ ZAZNACZONE", command=self.zakoncz_zadanie, cursor="hand2")
        self.button_finish.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.button_undo = ctk.CTkButton(self.tabview.tab("Twoja Lista"), text="ODZNACZ ZAZNACZONE", command=self.odznacz_zadanie, cursor="hand2")
        self.button_undo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.button_delete = ctk.CTkButton(self.tabview.tab("Twoja Lista"), text="USUŃ ZAZNACZONE", command=self.usun_zadanie, fg_color="red", cursor="hand2")
        self.button_delete.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.note_entry = ctk.CTkEntry(self.tabview.tab("Twoja Lista"), placeholder_text="Dodaj notatke...", width=300)
        self.note_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.button_note = ctk.CTkButton(self.tabview.tab("Twoja Lista"), text="DODAJ NOTATKE", command=self.dodaj_notatke, cursor="hand2")
        self.button_note.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        #Pasek postepu

        self.label_stats = ctk.CTkLabel(self.tabview.tab("Twoja Lista"), text="Postep: 0%")
        self.label_stats.grid(row=6, column=0, columnspan=2,pady=5, sticky ="ew")


        #Pasek Postepu Graficznie 

        self.progress_bar = ctk.CTkProgressBar(self.tabview.tab("Twoja Lista"),width=400 )
        self.progress_bar.grid(row=7, column=0, columnspan=3,pady=10, padx=20, sticky="ew"  )
        self.progress_bar.set(0)

        # --- PRZYCISK ZAPISU (NA DOLE) ---
        self.button_saveandquit = ctk.CTkButton(self, text="ZAPISZ I WYJDŹ", command=self.save_quit, fg_color="green", cursor="hand2")
        self.button_saveandquit.pack(pady=10, side="bottom")

        # --- WCZYTYWANIE(JSON) ---
        try:
            with open(SCIEZKA_PLIKU, "r", encoding="utf-8") as plik:
                
                data = json.load(plik)

                self.textbox.configure(state="normal")

                #Petla for 

                for zadanie in data:
                    tekst = zadanie.get("raw_text", "")
                    if tekst:
                        self.textbox.insert("end", f"{tekst}\n")

                self.textbox.configure(state="disabled")
        except FileNotFoundError:
            pass

        self.protocol("WM_DELETE_WINDOW", self.save_quit)
        self.odswiez_statystki()


    # Dodajemy Logike

    def dodaj_zadanie(self):
        zadanie = self.entry.get() #Pobieramy tekst z pola

        if zadanie:
            #Na razie dopisujemy do okna na ekranie
            self.textbox.configure(state="normal")

            self.textbox.insert("end", f"- {zadanie} \n")
            self.textbox.configure(state="disabled")
            self.entry.delete(0, 'end') # Czyscimy pole po dodaniu



            print(f"Dodano zadanie: {zadanie}")


            self.odswiez_statystki()


    def usun_zadanie(self):
        #sprawdzamy co zaznaczyłem
        try:
            wybrane = self.textbox.get("insert linestart", "insert lineend").strip()

            if not wybrane : 
                print("Nic nie zaznaczono")
                return
            
            
            #Pobieramy cała treść
            self.textbox.configure(state="normal") 
            tresc = self.textbox.get("1.0", "end")
            #Usuwamy tylko to ,co bylo zaznaczone
            nowa_tresc = tresc.replace(wybrane, "")
            

            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", nowa_tresc.strip())
            self.textbox.configure(state="disabled") 
            print(f"Usunieto : {wybrane}")

        except:
            print("Nic nie zaznaczono")
        self.odswiez_statystki()


    def zakoncz_zadanie(self):
        try:
            #1.Pobieramy cała linie 

            wybrane = self.textbox.get("insert linestart", "insert lineend").strip()
            
            #Generowanie czasu zakończenia

            czas_zakonczenia = datetime.now().strftime("%Y.%m.%d - %H.%M")


            if not wybrane : #Jesli nic nie zaznaczamy to nic nie robimy
                print("Nic nie zaznaczono")
                return
            
            self.textbox.configure(state="normal")
            tresc = self.textbox.get("1.0", "end")


            #Wycinamy stare i stary czas i jesli byly
            czyste = wybrane.replace("✅ ", "").replace("-", "").split("[")[0].strip()
            

            #Jesli to zadanie nie jest jeszcze zakonczone

            if "✅" not in wybrane:
                nowe = f"✅ {czyste} [ZAKONCZONE o {czas_zakonczenia}]"
                nowa_tresc = tresc.replace(wybrane, nowe)

                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", nowa_tresc.strip()+"\n")

            self.textbox.configure(state="disabled")
        except:
            print("Nic nie zaznaczono")

        self.odswiez_statystki()

    def odznacz_zadanie(self):
        try:
            wybrane = self.textbox.get("insert linestart", "insert lineend").strip()
            if not wybrane or "✅" not in wybrane: return

            self.textbox.configure(state="normal")
            tresc = self.textbox.get("1.0", "end")


            #Wycinamy wszystko po lewej i prawej stronie 
            #spslit("[]")[0] bierze tket przed nawaiasem z godziną 

            czyste = wybrane.replace("✅ ", "").replace("-", "").split("[")[0].strip()
            nowe = f"- {czyste}"
            nowa_tresc = tresc.replace(wybrane, nowe)

            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", nowa_tresc.strip()+"\n")
            self.textbox.configure(state="disabled")
            self.odswiez_statystki()
        except:
            print("Bład odznaczenia")

        

    
       
    def save_quit(self):
        #1.Pobieramy linie i zamienamy na liste słowników

        linie = self.textbox.get("1.0", "end").split("\n")

        data_to_save = []

        for l in linie:
            status = "done" if "✅" in l else "todo"
            #Tu uzwamy tuple do rozdzielenia daty

            data_to_save.append({"raw_text": l, "status": status})

        #2. Zapisujemy jak elegancki JSON

        with open(SCIEZKA_PLIKU, "w", encoding="utf-8") as plik:
            json.dump(data_to_save, plik, indent=4, ensure_ascii=False)

        self.destroy()


    def dodaj_notatke(self):
        try:
            #Pobieram dane wejsciowe
            wybrane = self.textbox.get("insert linestart", "insert lineend").strip()
            notatka = self.note_entry.get()

            if not wybrane or not notatka: return 

            self.textbox.configure(state="normal")
            tresc = self.textbox.get("1.0", "end")

            #Rozcinam linie zeby usunac stara notatke


            czyste_zadanie = wybrane.split("  |  ")[0].strip()

            #Skadlam nowa liniez notatka

            nowe = f"{czyste_zadanie}| Notatka : {notatka}"

            #Podmieniam tekst w calym oknie

            nowa_tresc = tresc.replace(wybrane, nowe)

            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", nowa_tresc.strip()+"\n")
            self.textbox.configure(state="disabled")

            #Czysce pole wpisywania notatki 

            self.note_entry.delete(0, "end")

            print(f"Dodano notatkę do : {czyste_zadanie}")

        except Exception as e:
            print("Bład dodawania notatki", {e})





    def odswiez_statystki(self):
        #Pobieram tetk i robie z niego tuple

        linie = self.textbox.get("1.0", "end-1c").split("\n")

        ile_zrobionych = 0
        ile_wszystkich = 0 

       
        #Petla for

        for linia in linie:
            czysta_linia=linia.strip()
            if czysta_linia:
                ile_wszystkich += 1
                if "✅" in czysta_linia:
                    ile_zrobionych += 1

        if ile_wszystkich >0:
            ulamek = (ile_zrobionych / ile_wszystkich) 

            self.progress_bar.set(ulamek)

            procent = ulamek * 100

            self.label_stats.configure(text= f"Postęp : {procent:.0f}% ({ile_zrobionych}/{ile_wszystkich})"
                                       )


        else:
            self.progress_bar.set(0)
            self.label_stats.configure(text="Dodaj pierwsze zadanie")



if __name__ == "__main__":
    app = DziennikZadan()
    app.mainloop()



        
