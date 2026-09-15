# [M] NanaZip: Stack out-of-bounds read in NanaZip ZealFS bitmap parser

## Summary
Severity: Medium
Advisory: CVE-2026-42446
Aliases: GHSA-4c79-hfr4-mqv9
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42446
Type: osv

## Details
NanaZip is an open source file archive. From 5.0.1252.0 to before 6.0.1698.0, a stack-based out-of-bounds read exists in the ZealFS filesystem image parser in NanaZip. The vulnerability is triggered when opening a crafted ZealFS v1 filesystem image. An attacker-controlled BitmapSize field in the file header drives an unbounded loop that reads past the end of a stack-allocated ZEALFS_V1_HEADER structure. This vulnerability is fixed in 6.0.1698.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42446.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-4c79-hfr4-mqv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42446
