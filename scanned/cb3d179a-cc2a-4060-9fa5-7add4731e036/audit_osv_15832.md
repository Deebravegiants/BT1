# [H] CVE-2019-19954

## Summary
Severity: High
Advisory: CVE-2019-19954
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19954
Type: osv

## Details
Signal Desktop before 1.29.1 on Windows allows local users to gain privileges by creating a Trojan horse %SYSTEMDRIVE%\node_modules\.bin\wmic.exe file.

## References
- https://blog.mirch.io/2019/12/18/signal-desktop-windows-lpe/
- https://github.com/signalapp/Signal-Desktop/commit/2da39cca673cc11be3c6d70d4fb95889f9ab6688
