# [C] CVE-2020-28024

## Summary
Severity: Critical
Advisory: CVE-2020-28024
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28024
Type: osv

## Details
Exim 4 before 4.94.2 allows Buffer Underwrite that may result in unauthenticated remote attackers executing arbitrary commands, because smtp_ungetc was only intended to push back characters, but can actually push back non-character error codes such as EOF.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28024-UNGET.txt
