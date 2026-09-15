# [H] CVE-2017-17845

## Summary
Severity: High
Advisory: CVE-2017-17845
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17845
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9. Improper Random Secret Generation occurs because Math.Random() is used by pretty Easy privacy (pEp), aka TBE-01-001.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://www.mail-archive.com/enigmail-users%40enigmail.net/msg04280.html
- https://enigmail.net/download/other/Enigmail%20Pentest%20Report%20by%20Cure53%20-%20Excerpt.pdf
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://www.debian.org/security/2017/dsa-4070
