# [M] Anubis: Policy bypass via client controlled X-Original-URI header

## Summary
Severity: Medium
Advisory: CVE-2026-62314
Aliases: GHSA-6wcg-mqvh-fcvg
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-62314
Type: osv

## Details
Anubis is a Web AI Firewall Utility that challenges users' connections in order to protect upstream resources from scraper bots. From 1.22.0 until 1.26.0-pre1, lib/policy/checker.go PathChecker.Check() trusted the client-controlled X-Original-URI header before matching r.URL.Path, allowing an HTTP client to match default data/common/keep-internet-working.yaml ALLOW rules such as ^/\.well-known/.*$ and bypass the Anubis challenge. This issue is fixed in version 1.26.0-pre1.

## References
- https://github.com/TecharoHQ/anubis/releases/tag/v1.26.0-pre1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62314.json
- https://github.com/TecharoHQ/anubis/security/advisories/GHSA-6wcg-mqvh-fcvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-62314
- https://github.com/TecharoHQ/anubis/commit/276b537776b281b1c4e01421435bc03ade3d8fc4
- https://github.com/TecharoHQ/anubis/pull/1630
