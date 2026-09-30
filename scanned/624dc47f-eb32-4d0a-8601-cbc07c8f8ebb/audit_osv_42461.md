# [C] HKUDS OpenHarness Plugin Management Command Exposure

## Summary
Severity: Critical
Advisory: CVE-2026-6819
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-6819
Type: osv

## Details
HKUDS OpenHarness prior to PR #156 remediation exposes plugin lifecycle commands including /plugin install, /plugin enable, /plugin disable, and /reload-plugins to remote senders by default. Attackers who gain access through the channel layer can remotely manage plugin trust and activation state, enabling unauthorized plugin installation and activation on the system.

## References
- https://github.com/HKUDS/OpenHarness/releases/tag/v0.1.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6819.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6819
- https://www.vulncheck.com/advisories/hkuds-openharness-plugin-management-command-exposure
- https://github.com/HKUDS/OpenHarness/pull/156
- https://github.com/HKUDS/OpenHarness/commit/59017e09880fcf9a6f60456a84fb982900b2c0b2
