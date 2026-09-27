# [H] CVE-2024-30202

## Summary
Severity: High
Advisory: CVE-2024-30202
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2024-30202
Type: osv

## Details
In Emacs before 29.3, arbitrary Lisp code is evaluated as part of turning on Org mode. This affects Org Mode before 9.6.23.

## References
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?h=emacs-29&id=befa9fcaae29a6c9a283ba371c3c5234c7f644eb
- https://git.savannah.gnu.org/cgit/emacs.git/tree/etc/NEWS?h=emacs-29
- https://git.savannah.gnu.org/cgit/emacs/org-mode.git/commit/?id=003ddacf1c8d869b1858181c29ea21b731a8d8d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30202.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-30202
- http://www.openwall.com/lists/oss-security/2024/03/25/2
- http://www.openwall.com/lists/oss-security/2024/04/08/6
