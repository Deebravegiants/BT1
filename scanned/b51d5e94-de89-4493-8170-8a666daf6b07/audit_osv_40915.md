# [M] CVE-2026-56136

## Summary
Severity: Medium
Advisory: CVE-2026-56136
Aliases: GHSA-r66g-c39x-cw95
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-56136
Type: osv

## Details
In NTFS-3G through 2026.2.25, an out-of-bounds read exists in ntfs_ir_nill() in libntfs-3g/index.c that allows an attacker to read possibly confidential information in an ntfs-3g process by crafting a malicious NTFS image. This read operation is triggered by creation of a file with a crafted name.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56136.json
- https://github.com/tuxera/ntfs-3g/security/advisories/GHSA-r66g-c39x-cw95
- https://nvd.nist.gov/vuln/detail/CVE-2026-56136
