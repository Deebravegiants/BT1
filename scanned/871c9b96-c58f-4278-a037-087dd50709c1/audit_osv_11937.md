# [C] CVE-2018-1000138

## Summary
Severity: Critical
Advisory: CVE-2018-1000138
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-03-23
Source: https://osv.dev/vulnerability/CVE-2018-1000138
Type: osv

## Details
I, Librarian version 4.8 and earlier contains a SSRF vulnerability in "url" parameter of getFromWeb in functions.php that can result in the attacker abusing functionality on the server to read or update internal resources.

## References
- https://github.com/mkucej/i-librarian/blob/9535753a84bc615b210802d4c9542db73368d984/functions.php#L811
- https://github.com/mkucej/i-librarian/issues/120
