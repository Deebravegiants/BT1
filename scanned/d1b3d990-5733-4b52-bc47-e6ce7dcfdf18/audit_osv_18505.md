# [H] CVE-2020-28019

## Summary
Severity: High
Advisory: CVE-2020-28019
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28019
Type: osv

## Details
Exim 4 before 4.94.2 has Improper Initialization that can lead to recursion-based stack consumption or other consequences. This occurs because use of certain getc functions is mishandled when a client uses BDAT instead of DATA.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28019-BDATA.txt
