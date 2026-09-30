# [H] Vibe-Trading < 0.1.10 - Path Traversal in Proposal Identifier Allows Forging Live Trading Mandates

## Summary
Severity: High
Advisory: CVE-2026-58170
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58170
Type: osv

## Details
Vibe-Trading before 0.1.10 builds the proposal file path by joining a caller-supplied proposal identifier onto the broker proposals directory without sanitization (agent/src/live/mandate/commit.py). A proposal identifier containing path traversal sequences causes the application to load an attacker-controlled JSON file as an authoritative live trading mandate. Combined with the file upload endpoint, an admitted caller can write a JSON file to a known location and traverse to it, and because the ceilings validation is skipped when ceilings are absent, the attacker fully controls the committed mandate.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58170.json
- https://github.com/HKUDS/Vibe-Trading/releases/tag/v0.1.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-58170
- https://www.vulncheck.com/advisories/vibe-trading-path-traversal-in-proposal-identifier-allows-forging-live-trading-mandates
- https://github.com/HKUDS/Vibe-Trading/pull/256
- https://github.com/HKUDS/Vibe-Trading/commit/0ab701302f90e701c9dc558a898a217a376610c3
- https://github.com/HKUDS/Vibe-Trading
