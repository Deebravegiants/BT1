# [M] CVE-2018-20431

## Summary
Severity: Medium
Advisory: CVE-2018-20431
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-24
Source: https://osv.dev/vulnerability/CVE-2018-20431
Type: osv

## Details
GNU Libextractor through 1.8 has a NULL Pointer Dereference vulnerability in the function process_metadata() in plugins/ole2_extractor.c.

## References
- http://www.securityfocus.com/bid/106300
- https://gnunet.org/git/libextractor.git/tree/ChangeLog
- https://lists.debian.org/debian-lts-announce/2018/12/msg00015.html
- https://www.debian.org/security/2018/dsa-4361
- https://gnunet.org/bugs/view.php?id=5494
- https://gnunet.org/git/libextractor.git/commit/?id=489c4a540bb2c4744471441425b8932b97a153e7
