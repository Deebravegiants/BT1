# [H] CVE-2021-44504

## Summary
Severity: High
Advisory: CVE-2021-44504
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44504
Type: osv

## Details
An issue was discovered in FIS GT.M through V7.0-000 (related to the YottaDB code base). Using crafted input, an attacker can cause a size variable, stored as an signed int, to equal an extremely large value, which is interpreted as a negative value during a check. This value is then used in a memcpy call on the stack, causing a memory segmentation fault.

## References
- http://tinco.pair.com/bhaskar/gtm/doc/articles/GTM_V7.0-002_Release_Notes.html
- https://sourceforge.net/projects/fis-gtm/files/
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
