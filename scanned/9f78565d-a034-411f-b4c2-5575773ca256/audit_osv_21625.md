# [M] CVE-2021-44590

## Summary
Severity: Medium
Advisory: CVE-2021-44590
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-44590
Type: osv

## Details
In libming 0.4.8, a memory exhaustion vulnerability exist in the function cws2fws in util/main.c. Remote attackers could launch denial of service attacks by submitting a crafted SWF file that exploits this vulnerability.

## References
- https://github.com/libming/libming
- https://github.com/libming/libming/issues/236
