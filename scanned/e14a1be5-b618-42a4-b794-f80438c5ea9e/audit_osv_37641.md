# [H] Cryptomator: Tampered vault configuration allows MITM attack on Hub API

## Summary
Severity: High
Advisory: CVE-2026-32303
Aliases: GHSA-34rf-rwr3-7g43
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32303
Type: osv

## Details
Cryptomator encrypts data being stored on cloud infrastructure. Prior to version 1.19.1, an integrity check vulnerability allows an attacker to tamper with the vault configuration file leading to a man-in-the-middle vulnerability in Hub key loading mechanism. Before this fix, the client trusted endpoints from the vault config without host authenticity checks, which could allow token exfiltration by mixing a legitimate auth endpoint with a malicious API endpoint. Impacted are users unlocking Hub-backed vaults with affected client versions in environments where an attacker can alter the vault.cryptomator file. This issue has been patched in version 1.19.1.

## References
- https://github.com/cryptomator/cryptomator/releases/tag/1.19.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32303.json
- https://github.com/cryptomator/cryptomator/security/advisories/GHSA-34rf-rwr3-7g43
- https://nvd.nist.gov/vuln/detail/CVE-2026-32303
- https://github.com/cryptomator/cryptomator/commit/6b82abcd80449a30b561d823193f9ecea542a625
- https://github.com/cryptomator/cryptomator/pull/4179
