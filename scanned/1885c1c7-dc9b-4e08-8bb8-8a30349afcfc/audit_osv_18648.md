# [M] CVE-2020-29562

## Summary
Severity: Medium
Advisory: CVE-2020-29562
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-29562
Type: osv

## Details
The iconv function in the GNU C Library (aka glibc or libc6) 2.30 to 2.32, when converting UCS4 text containing an irreversible character, fails an assertion in the code path and aborts the program, potentially resulting in a denial of service.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TVCUNLQ3HXGS4VPUQKWTJGRAW2KTFGXS/
- https://security.gentoo.org/glsa/202101-20
- https://security.netapp.com/advisory/ntap-20210122-0004/
- https://sourceware.org/bugzilla/show_bug.cgi?id=26923
