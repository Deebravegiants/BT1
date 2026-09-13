# [C] CVE-2020-10964

## Summary
Severity: Critical
Advisory: CVE-2020-10964
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-10964
Type: osv

## Details
Serendipity before 2.3.4 on Windows allows remote attackers to execute arbitrary code because the filename of a renamed file may end with a dot. This file may then be renamed to have a .php filename.

## References
- https://blog.s9y.org/archives/290-Serendipity-2.3.4-released-security-update.html
- https://github.com/s9y/Serendipity/releases/tag/2.3.4
