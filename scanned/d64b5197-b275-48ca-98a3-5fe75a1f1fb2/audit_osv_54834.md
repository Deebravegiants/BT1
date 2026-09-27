# [H] CVE-2024-48938

## Summary
Severity: High
Advisory: CVE-2024-48938
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-48938
Type: osv

## Details
Znuny before LTS 6.5.1 through 6.5.10 and 7.0.1 through 7.0.16 allows DoS/ReDos via email. Parsing the content of emails where HTML code is copied from Microsoft Word could lead to high CPU usage and block the parsing process.

## References
- https://www.znuny.com
- https://www.znuny.org/en/advisories
- https://www.znuny.org/en/advisories/zsa-2024-04
