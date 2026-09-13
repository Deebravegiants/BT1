# [M] NanaZip: Heap out-of-bounds write in NanaZip UFS directory parser

## Summary
Severity: Medium
Advisory: CVE-2026-44215
Aliases: GHSA-44wh-7gc3-w936
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44215
Type: osv

## Details
NanaZip is an open source file archive. From 5.0.1252.0 to before 6.0.1698.0, a one-byte heap out-of-bounds null write exists in the UFS/UFS2 filesystem image parser in NanaZip. The vulnerability is triggered when opening a crafted UFS filesystem image. The attacker controls the byte offset of the write within a ~254-byte window past the heap allocation boundary. This vulnerability is fixed in 6.0.1698.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44215.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-44wh-7gc3-w936
- https://nvd.nist.gov/vuln/detail/CVE-2026-44215
