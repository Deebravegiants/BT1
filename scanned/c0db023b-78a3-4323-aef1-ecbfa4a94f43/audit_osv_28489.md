# [H] nscd: netgroup cache assumes NSS callback uses in-buffer strings

## Summary
Severity: High
Advisory: CVE-2024-33602
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-33602
Type: osv

## Details
nscd: netgroup cache assumes NSS callback uses in-buffer strings

The Name Service Cache Daemon's (nscd) netgroup cache can corrupt memory
when the NSS callback does not store all strings in the provided buffer.
The flaw was introduced in glibc 2.15 when the cache was added to nscd.

This vulnerability is only present in the nscd binary.

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/5
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33602.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33602
- https://security.netapp.com/advisory/ntap-20240524-0012/
- https://sourceware.org/git/?p=glibc.git;a=blob;f=advisories/GLIBC-SA-2024-0008
