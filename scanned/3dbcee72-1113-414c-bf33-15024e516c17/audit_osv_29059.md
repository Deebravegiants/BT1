# [C] CVE-2024-39331

## Summary
Severity: Critical
Advisory: CVE-2024-39331
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-23
Source: https://osv.dev/vulnerability/CVE-2024-39331
Type: osv

## Details
In Emacs before 29.4, org-link-expand-abbrev in lisp/ol.el expands a %(...) link abbrev even when it specifies an unsafe function, such as shell-command-to-string. This affects Org Mode before 9.7.5.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/tree/etc/NEWS?h=emacs-29
- https://git.savannah.gnu.org/cgit/emacs/org-mode.git/commit/?id=f4cc61636947b5c2f0afc67174dd369fe3277aa8
- https://list.orgmode.org/87sex5gdqc.fsf%40localhost/
- https://lists.gnu.org/archive/html/info-gnu-emacs/2024-06/msg00000.html
- https://news.ycombinator.com/item?id=40768225
- https://www.openwall.com/lists/oss-security/2024/06/23/1
- https://www.openwall.com/lists/oss-security/2024/06/23/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39331.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39331
- https://lists.debian.org/debian-lts-announce/2024/06/msg00023.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00024.html
