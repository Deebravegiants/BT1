# [H] CVE-2021-44502

## Summary
Severity: High
Advisory: CVE-2021-44502
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44502
Type: osv

## Details
An issue was discovered in FIS GT.M through V7.0-000 (related to the YottaDB code base). Using crafted input, an attacker can control the size of a memset that occurs in calls to util_format in sr_unix/util_output.c.

## References
- http://tinco.pair.com/bhaskar/gtm/doc/articles/GTM_V7.0-002_Release_Notes.html
- https://sourceforge.net/projects/fis-gtm/files/
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
