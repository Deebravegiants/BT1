# [H] Misskey: TOTP tokens can be reused

## Summary
Severity: High
Advisory: CVE-2026-57574
Aliases: GHSA-2m5x-5mp6-6vpq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57574
Type: osv

## Details
Misskey is an open source, federated social media platform. Prior to 2026.6.0, Misskey contains a vulnerability in Time-based One-Time Password (TOTP) authentication in UserAuthService where insufficient validation of used tokens allows the reuse of a single-use code within its valid time step. If both credentials and a TOTP code are obtained concurrently, an attacker may reuse the code to perform unauthorized actions, potentially leading to account takeover. This issue is fixed in version 2026.6.0.

## References
- https://github.com/misskey-dev/misskey/releases/tag/2026.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57574.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-2m5x-5mp6-6vpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-57574
- https://github.com/misskey-dev/misskey/commit/00c6210a591db2b0be438740d05b82070fa68ac6
- https://github.com/misskey-dev/misskey/commit/d323fe00d04ac46ab0b4e66fce9169effaa8dfb7
