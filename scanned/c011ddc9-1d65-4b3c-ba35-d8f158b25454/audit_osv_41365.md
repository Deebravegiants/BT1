# [H] Cline: Cross-Origin WebSocket Hijacking in Cline Hub Dashboard (`/browser` endpoint)

## Summary
Severity: High
Advisory: CVE-2026-59723
Aliases: GHSA-3cj3-hqcr-g934
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59723
Type: osv

## Details
Cline is an autonomous coding agent as an SDK, IDE extension, or CLI assistant. Prior to 3.0.30, the Cline Hub dashboard server launched by the cline dashboard command accepts WebSocket connections on the /browser endpoint without validating the Origin header, and when ROOM_SECRET is unset for local 127.0.0.1 binds, isAuthorizedBrowserRequest() allows attacker-controlled websites to send desktopCommand frames that read workspace state, mutate MCP and provider settings, and trigger command execution when a provider or model is configured. This issue is fixed in version 3.0.30.

## References
- https://github.com/cline/cline/releases/tag/cli-v3.0.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59723.json
- https://github.com/cline/cline/security/advisories/GHSA-3cj3-hqcr-g934
- https://nvd.nist.gov/vuln/detail/CVE-2026-59723
- https://github.com/cline/cline/commit/d09270940f5746f288cfc4a5039b46a2f4d5d01e
- https://github.com/cline/cline/pull/11724
