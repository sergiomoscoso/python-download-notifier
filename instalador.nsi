; Script de instalador - Notificador de Descargas
; Compila con: "MakeNSIS instalador.nsi"

!include "MUI2.nsh"

;-----------------------
; Información del instalador
;-----------------------
Name "Notificador de Descargas"
Icon "icon.ico"
OutFile "NotificadorDeDescargas-Instalador.exe"
InstallDir "$PROGRAMFILES\Notificador de Descargas"
RequestExecutionLevel admin

;-----------------------
; Interfaz moderna
;-----------------------
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

;-----------------------
; Instalación
;-----------------------
Section "Instalar Notificador"
    SetOutPath "$INSTDIR"
    
    ; Copiar archivos
    File "dist\NotificadorDeDescargas.exe"
    File "config.json"
    File "icon.ico"

    ; Acceso directo en el escritorio
    CreateShortCut "$DESKTOP\Notificador de Descargas.lnk" "$INSTDIR\NotificadorDeDescargas.exe" "" "$INSTDIR\icon.ico"

    ; Menú de inicio
    CreateDirectory "$SMPROGRAMS\Notificador de Descargas"
    CreateShortCut "$SMPROGRAMS\Notificador de Descargas\Notificador.lnk" "$INSTDIR\NotificadorDeDescargas.exe" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\Notificador de Descargas\Desinstalar.lnk" "$INSTDIR\uninstall.exe"

    ; Crear desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Registro en el sistema (para desinstalar desde Panel de Control)
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NotificadorDeDescargas" "DisplayName" "Notificador de Descargas"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NotificadorDeDescargas" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NotificadorDeDescargas" "DisplayIcon" "$\"$INSTDIR\icon.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NotificadorDeDescargas" "Publisher" "Tu Nombre"
SectionEnd

;-----------------------
; Desinstalación
;-----------------------
Section "Desinstalar"
    Delete "$INSTDIR\NotificadorDeDescargas.exe"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\config.json"
    Delete "$INSTDIR\icon.ico"
    Delete "$DESKTOP\Notificador de Descargas.lnk"
    
    ; Eliminar menú de inicio
    Delete "$SMPROGRAMS\Notificador de Descargas\*.*"
    RMDir "$SMPROGRAMS\Notificador de Descargas"
    
    ; Eliminar carpeta de instalación
    RMDir "$INSTDIR"
    
    ; Eliminar del registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NotificadorDeDescargas"
SectionEnd