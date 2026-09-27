# [H] nscd: Stack-based buffer overflow in netgroup cache

## Summary
Severity: High
Advisory: CVE-2024-33599
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-33599
Type: osv

## Details
nscd: Stack-based buffer overflow in netgroup cache

If the Name Service Cache Daemon's (nscd) fixed size cache is exhausted
by client requests then a subsequent client request for netgroup data
may result in a stack-based buffer overflow.  This flaw was introduced
in glibc 2.15 when the cache was added to nscd.

This vulnerability is only present in the nscd binary.

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33599.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33599
- https://security.netapp.com/advisory/ntap-20240524-0011/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2024-0005
