# [C] CVE-2021-44496

## Summary
Severity: Critical
Advisory: CVE-2021-44496
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44496
Type: osv

## Details
An issue was discovered in FIS GT.M through V7.0-000 (related to the YottaDB code base). Using crafted input, an attacker can control the size variable and buffer that is passed to a call to memcpy. An attacker can use this to overwrite key data structures and gain control of the flow of execution.

## References
- http://tinco.pair.com/bhaskar/gtm/doc/articles/GTM_V7.0-002_Release_Notes.html
- https://sourceforge.net/projects/fis-gtm/files/
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
