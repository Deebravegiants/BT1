# [H] CVE-2021-44497

## Summary
Severity: High
Advisory: CVE-2021-44497
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44497
Type: osv

## Details
An issue was discovered in FIS GT.M through V7.0-000 (related to the YottaDB code base). Using crafted input, can cause the bounds of a for loop to be miscalculated, which leads to a use after free condition a pointer is pushed into previously free memory by the loop.

## References
- http://tinco.pair.com/bhaskar/gtm/doc/articles/GTM_V7.0-002_Release_Notes.html
- https://sourceforge.net/projects/fis-gtm/files/
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
