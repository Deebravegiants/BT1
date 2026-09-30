# [M] CodeWhale before 0.8.64 Arbitrary File Read via instructions

## Summary
Severity: Medium
Advisory: CVE-2026-75859
Aliases: GHSA-62f5-cp2p-vq95
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75859
Type: osv

## Details
CodeWhale versions before 0.8.64 fail to validate file paths in the project config instructions field, allowing attackers to read arbitrary files on the victim's system. A malicious .codewhale/config.toml file in a cloned repository can specify paths outside the workspace that are read and injected into the AI system prompt for exfiltration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75859.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-62f5-cp2p-vq95
- https://nvd.nist.gov/vuln/detail/CVE-2026-75859
- https://www.vulncheck.com/advisories/codewhale-before-arbitrary-file-read-via-instructions
- https://github.com/Hmbown/CodeWhale/commit/43563356b98c6b993085554da82e77370160a31c
