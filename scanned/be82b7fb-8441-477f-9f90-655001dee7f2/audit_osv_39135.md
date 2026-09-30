# [C] OpenClaw <  2026.4.15 - Authorization Bypass in Matrix Room Control Commands via DM Pairing Store

## Summary
Severity: Critical
Advisory: CVE-2026-44110
Aliases: GHSA-2gvc-4f3c-2855
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-44110
Type: osv

## Details
OpenClaw before 2026.4.15 contains an authorization bypass vulnerability in Matrix room control-command authorization that trusts DM pairing-store entries. Attackers with DM-paired sender IDs can execute room control commands without being in configured allowlists by posting in bot rooms, potentially enabling privileged OpenClaw behavior.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44110.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2gvc-4f3c-2855
- https://nvd.nist.gov/vuln/detail/CVE-2026-44110
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-matrix-room-control-commands-via-dm-pairing-store
- https://github.com/openclaw/openclaw/commit/2bfd808a83116bd888e3e2633a61473fa2ed81b6
- https://github.com/openclaw/openclaw/commit/f8705f512b09043df02b5da372c33374734bd921
