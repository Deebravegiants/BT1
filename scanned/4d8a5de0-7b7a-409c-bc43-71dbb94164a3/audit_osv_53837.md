# [H] CVE-2023-27986

## Summary
Severity: High
Advisory: CVE-2023-27986
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2023-27986
Type: osv

## Details
emacsclient-mail.desktop in Emacs 28.1 through 28.2 is vulnerable to Emacs Lisp code injections through a crafted mailto: URI with unescaped double-quote characters. It is fixed in 29.0.90.

## References
- https://www.gabriel.urdhr.fr/2023/06/08/emacsclient-mail-shell-elisp-injections/
- http://www.openwall.com/lists/oss-security/2023/03/09/1
- https://www.openwall.com/lists/oss-security/2023/03/08/2
- http://git.savannah.gnu.org/cgit/emacs.git/commit/?h=emacs-29&id=3c1693d08b0a71d40a77e7b40c0ebc42dca2d2cc
