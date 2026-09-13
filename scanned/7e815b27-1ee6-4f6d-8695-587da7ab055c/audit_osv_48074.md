# [H] CVE-2017-17847

## Summary
Severity: High
Advisory: CVE-2017-17847
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17847
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9. Signature spoofing is possible because the UI does not properly distinguish between an attachment signature, and a signature that applies to the entire containing message, aka TBE-01-021. This is demonstrated by an e-mail message with an attachment that is a signed e-mail message in message/rfc822 format.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://www.mail-archive.com/enigmail-users%40enigmail.net/msg04280.html
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://sourceforge.net/p/enigmail/bugs/709/
- https://www.debian.org/security/2017/dsa-4070
- https://enigmail.net/download/other/Enigmail%20Pentest%20Report%20by%20Cure53%20-%20Excerpt.pdf
