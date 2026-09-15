# [H] OpenClaw has two SSRF via sendMediaFeishu and markdown image fetching in Feishu extension

## Summary
Severity: High
Advisory: GHSA-x22m-j5qq-j49m
CVE: CVE-2026-28451
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-x22m-j5qq-j49m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary
The Feishu extension could fetch attacker-controlled remote URLs in two paths without SSRF protections:

- `sendMediaFeishu(mediaUrl)`
- Feishu DocX markdown image URLs (write/append -> image processing)

### Affected versions
- `< 2026.2.14`

### Patched versions
- `>= 2026.2.14`

### Impact
If an attacker can influence tool calls (directly or via prompt injection), they may be able to trigger requests to internal services and re-upload the response as Feishu media.

### Remediation
Upgrade to OpenClaw `2026.2.14` or newer.

### Notes
The fix routes Feishu remote media fetching through hardened runtime helpers that enforce SSRF policies and size limits.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x22m-j5qq-j49m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28451
- https://github.com/openclaw/openclaw/pull/16285
- https://github.com/openclaw/openclaw/commit/5b4121d6011a48c71e747e3c18197f180b872c5d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-ssrf-via-feishu-extension-media-fetching
