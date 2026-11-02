# LuauPilot - Terms of use / Regulamin

Version Alpha 0.03 · Author: MaciekGos (https://github.com/MaciekGos)

> **Note: LuaPilot is now LuauPilot.** The project was renamed because LuaPilot.com already exists and provides a very similar product. The repository, application and branding are being updated to the new name, so the GitHub repository and some file names still say LuaPilot for now. The project itself is not discontinued.
>
> **Uwaga: LuaPilot nazywa się teraz LuauPilot.** Projekt zmienił nazwę, ponieważ istnieje już LuaPilot.com, który oferuje bardzo podobny produkt. Repozytorium, aplikacja i branding są aktualizowane do nowej nazwy, więc repozytorium GitHub i niektóre nazwy plików na razie nadal zawierają LuaPilot. Sam projekt nie został porzucony.

**Polski:** [przejdź do regulaminu](#regulamin-polski) · **English:** below

---

## Terms of use (English)

### 1. What LuauPilot is and how it works
LuauPilot has three parts that run on your own computer:

1. **A browser extension** (Chrome/Edge, loaded as an unpacked extension). On the DeepSeek chat page it reads the AI's replies. When a reply contains a command block (`@@LPCALL@@` or `@@LPLUA@@` ... `@@LPEND@@`), the extension sends the command to the bridge and types the result back into the chat as the next message. It also tidies the chat (shows commands as small chips) and can show a preview of screenshots.
2. **A bridge** (`bridge.py`), a small local program that listens on `127.0.0.1` only and passes commands to Roblox Studio's own MCP server, which is started as a child process.
3. **A desktop app** (Windows) that starts and watches the bridge, lives in the tray and can optionally open the AI site and Roblox Studio when it starts.

Commands the AI sends run in your open Roblox Studio place. They can create, change and **delete** instances and scripts. Nothing is sent to the author; the extension talks to the chat site you are already using and to the bridge on your own machine.

### 2. Use at your own risk
You use LuauPilot entirely at your own risk. An AI can make mistakes, misread your request or delete or overwrite your work. Keep backups and version history of your places, and review what the AI does. The author is not responsible for lost or damaged work, banned or limited accounts, rate limits, costs, or any other damage resulting from the use of LuauPilot, to the extent permitted by law.

### 3. "As is", no support
LuauPilot is provided **"as is"**, without any warranty. The author has **no obligation** to provide support, fixes, updates or compatibility with future versions of the chat site, Roblox Studio or browsers. Chat websites change often, so parts of LuauPilot may stop working at any time.

### 4. Reporting bugs
You may report bugs on the project's GitHub Issues page. Reports are welcome, but they come with **no guarantee** of an answer, a fix or a time frame.

### 5. Inspiration and independence
The working principle of LuauPilot (a browser extension and a local bridge that let a chat AI drive Roblox Studio through MCP) is **inspired by ZeroScript**. The author of LuauPilot is **not affiliated with ZeroScript** or its authors in any way. LuauPilot's code was written separately and is not a copy of that project.

### 6. No affiliation with AI providers
The author is **not affiliated with the creators of any AI**, and not with any AI, chat service, model, Roblox Corporation or any other company named in or used with LuauPilot. All names and trademarks belong to their owners and are used only to describe compatibility. LuauPilot is not endorsed by any of them. You are responsible for following the terms of the chat service and of Roblox that apply to you.

### 7. License
The source code is released under the MIT License (see `LICENSE`). These terms describe how the software is meant to be used and do not limit the rights that license gives you.

---

## Regulamin (polski)

### 1. Czym jest LuauPilot i jak działa
LuauPilot składa się z trzech części, które działają na Twoim komputerze:

1. **Rozszerzenie przeglądarki** (Chrome/Edge, ładowane jako rozpakowane). Na stronie czatu DeepSeek czyta odpowiedzi AI. Gdy odpowiedź zawiera blok polecenia (`@@LPCALL@@` lub `@@LPLUA@@` ... `@@LPEND@@`), rozszerzenie wysyła polecenie do bridge'a, a wynik wpisuje z powrotem do czatu jako kolejną wiadomość. Porządkuje też wygląd czatu (polecenia jako małe „chipy") i potrafi pokazać podgląd zrzutów ekranu.
2. **Bridge** (`bridge.py`) - mały lokalny program nasłuchujący wyłącznie na `127.0.0.1`, który przekazuje polecenia do serwera MCP Roblox Studio uruchamianego jako proces potomny.
3. **Aplikacja desktopowa** (Windows), która uruchamia i pilnuje bridge'a, siedzi w zasobniku i opcjonalnie przy starcie otwiera stronę AI oraz Roblox Studio.

Polecenia wysyłane przez AI wykonują się w otwartym miejscu (place) w Roblox Studio. Mogą tworzyć, zmieniać i **usuwać** obiekty oraz skrypty. Nic nie jest wysyłane do autora; rozszerzenie komunikuje się ze stroną czatu, z której i tak korzystasz, oraz z bridge'em na Twoim komputerze.

### 2. Używasz na własną odpowiedzialność
Z LuauPilota korzystasz w całości na własną odpowiedzialność. AI może się mylić, źle zrozumieć polecenie albo usunąć lub nadpisać Twoją pracę. Rób kopie zapasowe i korzystaj z historii wersji swoich place'ów oraz sprawdzaj, co robi AI. Autor nie odpowiada za utracone lub uszkodzone prace, zablokowane lub ograniczone konta, limity, koszty ani inne szkody wynikające z używania LuauPilota - w zakresie dozwolonym przez prawo.

### 3. „As is", bez wsparcia
LuauPilot jest udostępniany **„tak jak jest" (as is)**, bez jakiejkolwiek gwarancji. Autor **nie ma obowiązku** udzielania wsparcia, poprawek, aktualizacji ani zgodności z przyszłymi wersjami serwisu czatu, Roblox Studio czy przeglądarek. Strony czatów często się zmieniają, więc części LuauPilota mogą w każdej chwili przestać działać.

### 4. Zgłaszanie błędów
Błędy można zgłaszać w zakładce GitHub Issues projektu. Zgłoszenia są mile widziane, ale **nic nie gwarantują**: ani odpowiedzi, ani poprawki, ani terminu.

### 5. Inspiracja i niezależność
Zasada działania LuauPilota (rozszerzenie przeglądarki i lokalny bridge, dzięki którym czat AI steruje Roblox Studio przez MCP) jest **inspirowana ZeroScript**. Autor LuauPilota **nie jest w żaden sposób powiązany z ZeroScript** ani z jego twórcami. Kod LuauPilota został napisany osobno i nie jest kopią tamtego projektu.

### 6. Brak powiązań z twórcami AI
Autor **nie jest powiązany z twórcami żadnego AI**, z żadnym AI, serwisem czatu, modelem, firmą Roblox Corporation ani żadną inną firmą wymienioną w LuaPilocie lub używaną razem z nim. Wszystkie nazwy i znaki towarowe należą do ich właścicieli i służą wyłącznie opisaniu zgodności. LuauPilot nie jest przez nikogo z nich wspierany ani rekomendowany. Odpowiadasz za przestrzeganie regulaminów serwisu czatu i Roblox, które Cię dotyczą.

### 7. Licencja
Kod źródłowy jest udostępniony na licencji MIT (plik `LICENSE`). Ten regulamin opisuje zamierzony sposób użycia i nie ogranicza praw, które daje Ci ta licencja.
