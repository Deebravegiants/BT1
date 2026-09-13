# [H] CVE-2022-29458

## Summary
Severity: High
Advisory: CVE-2022-29458
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2022-29458
Type: osv

## Details
ncurses 6.3 before patch 20220416 has an out-of-bounds read and segmentation violation in convert_strings in tinfo/read_entry.c in the terminfo library.

## References
- https://lists.gnu.org/archive/html/bug-ncurses/2022-04/msg00014.html
- https://lists.gnu.org/archive/html/bug-ncurses/2022-04/msg00016.html
- https://support.apple.com/kb/HT213488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29458.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29458
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://lists.debian.org/debian-lts-announce/2022/10/msg00037.html
