# [M] CVE-2025-0395

## Summary
Severity: Medium
Advisory: CVE-2025-0395
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2025-0395
Type: osv

## Details
When the assert() function in the GNU C Library versions 2.13 to 2.40 fails, it does not allocate enough space for the assertion failure message string and size information, which may lead to a buffer overflow if the message string size aligns to page size.

## References
- http://www.openwall.com/lists/oss-security/2025/01/22/4
- http://www.openwall.com/lists/oss-security/2025/01/23/2
- http://www.openwall.com/lists/oss-security/2025/04/13/1
- http://www.openwall.com/lists/oss-security/2025/04/24/7
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00039.html
- https://sourceware.org/pipermail/libc-announce/2025/000044.html
- https://www.openwall.com/lists/oss-security/2025/01/22/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0395.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0395
- https://security.netapp.com/advisory/ntap-20250228-0006/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2025-0001
- https://sourceware.org/bugzilla/show_bug.cgi?id=32582
