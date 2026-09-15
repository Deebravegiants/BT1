# [H] CVE-2023-27985

## Summary
Severity: High
Advisory: CVE-2023-27985
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2023-27985
Type: osv

## Details
emacsclient-mail.desktop in Emacs 28.1 through 28.2 is vulnerable to shell command injections through a crafted mailto: URI. This is related to lack of compliance with the Desktop Entry Specification. It is fixed in 29.0.90

## References
- https://www.gabriel.urdhr.fr/2023/06/08/emacsclient-mail-shell-elisp-injections/
- http://git.savannah.gnu.org/cgit/emacs.git/commit/?h=emacs-29&id=d32091199ae5de590a83f1542a01d75fba000467
- http://www.openwall.com/lists/oss-security/2023/03/09/1
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=60204
- https://www.openwall.com/lists/oss-security/2023/03/08/2
