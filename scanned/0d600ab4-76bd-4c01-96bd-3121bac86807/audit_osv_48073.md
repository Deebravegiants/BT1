# [H] CVE-2017-17846

## Summary
Severity: High
Advisory: CVE-2017-17846
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17846
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9. Regular expressions are exploitable for Denial of Service, because of attempts to match arbitrarily long strings, aka TBE-01-003.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://www.mail-archive.com/enigmail-users%40enigmail.net/msg04280.html
- https://enigmail.net/download/other/Enigmail%20Pentest%20Report%20by%20Cure53%20-%20Excerpt.pdf
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://www.debian.org/security/2017/dsa-4070
