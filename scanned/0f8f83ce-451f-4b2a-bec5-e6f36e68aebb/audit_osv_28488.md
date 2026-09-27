# [H] nscd: netgroup cache may terminate daemon on memory allocation failure

## Summary
Severity: High
Advisory: CVE-2024-33601
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-33601
Type: osv

## Details
nscd: netgroup cache may terminate daemon on memory allocation failure

The Name Service Cache Daemon's (nscd) netgroup cache uses xmalloc or
xrealloc and these functions may terminate the process due to a memory
allocation failure resulting in a denial of service to the clients.  The
flaw was introduced in glibc 2.15 when the cache was added to nscd.

This vulnerability is only present in the nscd binary.

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33601.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33601
- https://security.netapp.com/advisory/ntap-20240524-0014/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2024-0007
