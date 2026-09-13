# [H] OpenClaw has a local file disclosure via sendMediaFeishu in Feishu extension

## Summary
Severity: High
Advisory: GHSA-8jpq-5h99-ff5r
CVE: CVE-2026-26321
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-8jpq-5h99-ff5r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary
The Feishu extension previously allowed `sendMediaFeishu` to treat attacker-controlled `mediaUrl` values as local filesystem paths and read them directly.

### Affected versions
- `< 2026.2.14`

### Patched versions
- `>= 2026.2.14`

### Impact
If an attacker can influence tool calls (directly or via prompt injection), they may be able to exfiltrate local files by supplying paths such as `/etc/passwd` as `mediaUrl`.

### Remediation
Upgrade to OpenClaw `2026.2.14` or newer.

### Notes
The fix removes direct local file reads from this path and routes media loading through hardened helpers that enforce local-root restrictions.

---

Fix commit 5b4121d60 confirmed on main and in v2026.2.14. Upgrade to `openclaw >= 2026.2.14`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8jpq-5h99-ff5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26321
- https://github.com/openclaw/openclaw/commit/5b4121d6011a48c71e747e3c18197f180b872c5d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
