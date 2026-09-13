# [M] Grav before 2.0.1 Decompression Bomb via ZipArchiver

## Summary
Severity: Medium
Advisory: CVE-2026-61455
Aliases: CVE-2026-61690, GHSA-928x-9mpw-8h56
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61455
Type: osv

## Details
Grav before 2.0.1 contains a decompression bomb vulnerability in ZipArchiver::extract() that lacks limits on uncompressed size, file count, and nesting depth. Attackers can supply a crafted ZIP archive that expands to fill available disk space, causing denial of service by exhausting storage resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61455.json
- https://github.com/getgrav/grav/security/advisories/GHSA-928x-9mpw-8h56
- https://nvd.nist.gov/vuln/detail/CVE-2026-61455
- https://www.vulncheck.com/advisories/grav-before-decompression-bomb-via-ziparchiver
