@echo off
chcp 65001 > nul

set /p required_terms="Geben Sie die Pflichtbegriffe ein (Komma getrennt): "
set /p or_terms="Geben Sie alternative Begriffe ein (Komma getrennt): "
set /p not_terms="Geben Sie auszuschließende Begriffe ein (Komma getrennt): "

:select_mode
echo Wollen Sie eine Suche nach Start- und Endjahr oder nach den letzten N Jahren durchführen?
choice /C SE /M "Drücken Sie S für Start-/Endjahr oder E für die letzten N Jahre"
if errorlevel 2 goto last_n_years
if errorlevel 1 goto start_end_years

:start_end_years
set /p start_year="Startjahr der Suche: "
set /p end_year="Endjahr der Suche: "
if "%start_year%"=="" (
    goto start_end_years
)
if "%end_year%"=="" (
    goto start_end_years
)
set last_n_years=
goto continue

:last_n_years
set /p last_n_years="Anzahl der letzten Jahre für die Suche: "
if "%last_n_years%"=="" (
    echo [WARNUNG] Sie müssen eine Zahl für die letzten N Jahre eingeben!
    goto last_n_years
)
set start_year=
set end_year=

:continue
set /p limit="Maximale Anzahl der Ergebnisse: "
if "%limit%"=="" (
    echo [WARNUNG] Bitte geben Sie eine maximale Anzahl an Ergebnissen ein!
    goto continue
)

set /p open_access_only="Nur Open Access? (ja/nein): "
if /I not "%open_access_only%"=="ja" if /I not "%open_access_only%"=="nein" (
    echo [WARNUNG] Bitte geben Sie 'ja' oder 'nein' ein!
    goto continue
)

set /p pdf_available_only="Nur mit PDF? (ja/nein): "
if /I not "%pdf_available_only%"=="ja" if /I not "%pdf_available_only%"=="nein" (
    echo [WARNUNG] Bitte geben Sie 'ja' oder 'nein' ein!
    goto continue
)

python main.py "%required_terms%" "%or_terms%" "%not_terms%" "%start_year%" "%end_year%" "%last_n_years%" "%limit%" "%open_access_only%" "%pdf_available_only%"
pause
