# [H] CVE-2026-53689

## Summary
Severity: High
Advisory: CVE-2026-53689
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53689
Type: osv

## Details
libnfs through 6.0.2 before 55c18ea does not validate a string size, leading to an integer overflow during a connection to a crafted NFS server. This occurs in libnfs_zdr_string in lib/libnfs-zdr.c.

## References
- https://lists.debian.org/debian-lts-announce/2026/07/msg00031.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53689.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53689
- https://github.com/sahlberg/libnfs/commit/55c18ea33a83d667f79f0ef209c96895795c729f
