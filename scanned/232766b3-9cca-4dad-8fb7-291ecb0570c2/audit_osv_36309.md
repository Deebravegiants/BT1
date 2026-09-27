# [M] GuardDog Zip Bomb Vulnerability in safe_extract() Allows DoS

## Summary
Severity: Medium
Advisory: CVE-2026-22870
Aliases: GHSA-ffj4-jq7m-9g6v, PYSEC-2026-1429
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2026-22870
Type: osv

## Details
GuardDog is a CLI tool to identify malicious PyPI packages. Prior to 2.7.1, GuardDog's safe_extract() function does not validate decompressed file sizes when extracting ZIP archives (wheels, eggs), allowing attackers to cause denial of service through zip bombs. A malicious package can consume gigabytes of disk space from a few megabytes of compressed data. This vulnerability is fixed in 2.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22870.json
- https://github.com/DataDog/guarddog/security/advisories/GHSA-ffj4-jq7m-9g6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-22870
- https://github.com/DataDog/guarddog/commit/c3fb07b4838945f42497e78b7a02bcfb1e63969b
