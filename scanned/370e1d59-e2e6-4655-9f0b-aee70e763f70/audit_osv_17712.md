# [M] CVE-2020-19187

## Summary
Severity: Medium
Advisory: CVE-2020-19187
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-19187
Type: osv

## Details
Buffer Overflow vulnerability in fmt_entry function in progs/dump_entry.c:1100 in ncurses 6.1 allows remote attackers to cause a denial of service via crafted command.

## References
- http://seclists.org/fulldisclosure/2023/Dec/10
- http://seclists.org/fulldisclosure/2023/Dec/11
- http://seclists.org/fulldisclosure/2023/Dec/9
- https://support.apple.com/kb/HT214036
- https://support.apple.com/kb/HT214037
- https://support.apple.com/kb/HT214038
- https://security.netapp.com/advisory/ntap-20231006-0005/
- https://github.com/zjuchenyuan/fuzzpoc/blob/master/infotocap_poc3.md
