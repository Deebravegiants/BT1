# [M] Grav before 2.0.2 Decompression Bomb via Forged ZIP Size

## Summary
Severity: Medium
Advisory: CVE-2026-61449
Aliases: GHSA-8h9x-89f2-m7x3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61449
Type: osv

## Details
Grav 2.0.1 contains a decompression-bomb size-cap bypass in ZipArchiver and GPM\Installer. The size bound introduced in 2.0.1 sums the uncompressed size declared in each entry's ZIP central-directory header (ZipArchive::statIndex()['size']) and rejects archives exceeding system.gpm.archive.max_uncompressed_size before extraction. Because this declared size is attacker-forgeable and is not cross-checked against the actual inflated stream, a crafted archive declaring tiny per-entry sizes passes the cap while extractTo() writes the real, much larger content, filling disk or exhausting inodes. The archive must be supplied by a package source or admin upload (admin/operator trust). Fixed in 2.0.2. This is an incomplete fix for GHSA-928x-9mpw-8h56.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61449.json
- https://github.com/getgrav/grav/security/advisories/GHSA-8h9x-89f2-m7x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-61449
- https://www.vulncheck.com/advisories/grav-before-decompression-bomb-via-forged-zip-size
