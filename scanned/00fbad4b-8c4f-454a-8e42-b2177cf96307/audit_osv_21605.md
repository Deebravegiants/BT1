# [H] CVE-2021-44500

## Summary
Severity: High
Advisory: CVE-2021-44500
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44500
Type: osv

## Details
An issue was discovered in FIS GT.M through V7.0-000 (related to the YottaDB code base). A lack of input validation in calls to eb_div in sr_port/eb_muldiv.c allows attackers to crash the application by performing a divide by zero.

## References
- http://tinco.pair.com/bhaskar/gtm/doc/articles/GTM_V7.0-002_Release_Notes.html
- https://sourceforge.net/projects/fis-gtm/files/
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
