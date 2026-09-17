# [M] CVE-2017-17843

## Summary
Severity: Medium
Advisory: CVE-2017-17843
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17843
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9 that allows remote attackers to trigger use of an intended public key for encryption, because incorrect regular expressions are used for extraction of an e-mail address from a comma-separated list, as demonstrated by a modified Full Name field and a homograph attack, aka TBE-01-002.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://www.mail-archive.com/enigmail-users%40enigmail.net/msg04280.html
- https://enigmail.net/download/other/Enigmail%20Pentest%20Report%20by%20Cure53%20-%20Excerpt.pdf
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://www.debian.org/security/2017/dsa-4070
