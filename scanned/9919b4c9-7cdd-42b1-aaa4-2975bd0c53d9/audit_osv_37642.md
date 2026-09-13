# [H] Cryptomator: Hub unlocking accepts plaintext HTTP and unvalidated endpoint schemes

## Summary
Severity: High
Advisory: CVE-2026-32309
Aliases: GHSA-vv33-h7qx-c264
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32309
Type: osv

## Details
Cryptomator encrypts data being stored on cloud infrastructure. Prior to version 1.19.1, the Hub-based unlock flow explicitly supports hub+http and consumes Hub endpoints from vault metadata without enforcing HTTPS. As a result, a vault configuration can drive OAuth and key-loading traffic over plaintext HTTP or other insecure endpoint combinations. An active network attacker can tamper with or observe this traffic. Even when the vault key is encrypted for the device, bearer tokens and endpoint-level trust decisions are still exposed to downgrade and interception. This issue has been patched in version 1.19.1.

## References
- https://github.com/cryptomator/cryptomator/releases/tag/1.19.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32309.json
- https://github.com/cryptomator/cryptomator/security/advisories/GHSA-vv33-h7qx-c264
- https://nvd.nist.gov/vuln/detail/CVE-2026-32309
