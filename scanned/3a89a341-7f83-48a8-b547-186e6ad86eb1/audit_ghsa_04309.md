# [M] Hermes Agent creates response_store.db and webhook_subscriptions.json with world-readable permissions (mode 0o644)

## Summary
Severity: Medium
Advisory: GHSA-99f9-j8r3-p853
CVE: CVE-2026-53870
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-99f9-j8r3-p853
Type: github-advisory

## Affected
- PyPI: `hermes-agent` — affected >=0 <0.16.0

## Details
Hermes Agent before 0.16.0 creates response_store.db and webhook_subscriptions.json with world-readable permissions (mode 0o644), exposing conversation history and HMAC secrets to local users. Attackers with local filesystem access can read these files directly to obtain sensitive data including conversation history, tool payloads, prompts, and per-route HMAC secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53870
- https://github.com/NousResearch/hermes-agent/pull/30917
- https://github.com/NousResearch/hermes-agent/pull/31469
- https://github.com/NousResearch/hermes-agent/commit/3bace071bfadf2d2bec2ee048471a31ec920e3e8
- https://github.com/NousResearch/hermes-agent
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5
- https://www.vulncheck.com/advisories/hermes-agent-sensitive-file-permission-vulnerability-in-store-files
