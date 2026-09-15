# [M] CVE-2018-14616

## Summary
Severity: Medium
Advisory: CVE-2018-14616
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-14616
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.10. There is a NULL pointer dereference in fscrypt_do_page_crypto() in fs/crypto/crypto.c when operating on a file in a corrupted f2fs image.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- http://www.securityfocus.com/bid/104917
- https://bugzilla.kernel.org/show_bug.cgi?id=200465
