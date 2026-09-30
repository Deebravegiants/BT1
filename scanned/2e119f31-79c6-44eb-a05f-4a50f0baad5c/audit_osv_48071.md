# [M] CVE-2017-17844

## Summary
Severity: Medium
Advisory: CVE-2017-17844
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17844
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9. A remote attacker can obtain cleartext content by sending an encrypted data block (that the attacker cannot directly decrypt) to a victim, and relying on the victim to automatically decrypt that block and then send it back to the attacker as quoted text, aka the TBE-01-005 "replay" issue.

## References
- https://www.mail-archive.com/enigmail-users%40enigmail.net/msg04280.html
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://enigmail.net/download/other/Enigmail%20Pentest%20Report%20by%20Cure53%20-%20Excerpt.pdf
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://www.debian.org/security/2017/dsa-4070
