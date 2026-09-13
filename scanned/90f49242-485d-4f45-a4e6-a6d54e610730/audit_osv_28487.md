# [M] nscd: Null pointer crashes after notfound response

## Summary
Severity: Medium
Advisory: CVE-2024-33600
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-33600
Type: osv

## Details
nscd: Null pointer crashes after notfound response

If the Name Service Cache Daemon's (nscd) cache fails to add a not-found
netgroup response to the cache, the client request can result in a null
pointer dereference.  This flaw was introduced in glibc 2.15 when the
cache was added to nscd.

This vulnerability is only present in the nscd binary.

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33600.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33600
- https://security.netapp.com/advisory/ntap-20240524-0013/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2024-0006
