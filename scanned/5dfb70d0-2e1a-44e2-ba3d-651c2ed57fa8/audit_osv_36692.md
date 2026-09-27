# [H] Runtipi vulnerable to unauthenticated docker-compose.yml Overwrite via Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-25116
Aliases: GHSA-mwg8-x997-cqw6
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-25116
Type: osv

## Details
Runtipi is a personal homeserver orchestrator. Starting in version 4.5.0 and prior to version 4.7.2, an unauthenticated Path Traversal vulnerability in the `UserConfigController` allows any remote user to overwrite the system's `docker-compose.yml` configuration file. By exploiting insecure URN parsing, an attacker can replace the primary stack configuration with a malicious one, resulting in full Remote Code Execution (RCE) and host filesystem compromise the next time the instance is restarted by the operator. Version 4.7.2 fixes the vulnerability.

## References
- https://github.com/runtipi/runtipi/releases/tag/v4.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25116.json
- https://github.com/runtipi/runtipi/security/advisories/GHSA-mwg8-x997-cqw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-25116
