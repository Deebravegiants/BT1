# [M] OpenClaw has a Web Fetch DoS via unbounded response parsing

## Summary
Severity: Medium
Advisory: GHSA-p536-vvpp-9mc8
CVE: CVE-2026-28394
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-p536-vvpp-9mc8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
### Summary
The `web_fetch` tool could be used to crash the OpenClaw Gateway process (OOM / resource exhaustion) by fetching and attempting to parse attacker-controlled web pages with oversized response bodies or pathological HTML nesting.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.14`
- Fixed versions: `>= 2026.2.15`

### Impact
An attacker can social-engineer a user (or any automation that uses `web_fetch`) into fetching a malicious URL that returns extremely large or deeply nested HTML. The Gateway may exhaust memory or become unresponsive, causing a denial of service.

### Fix
The Gateway now caps the downloaded response body size before any HTML parsing and adds additional guards to avoid running Readability/DOM parsing on pathological HTML.

### Fix Commit(s)
- 166cf6a3e04c7df42bea70a7ad5ce2b9df46d147

### Release Process Note
This advisory is prepared for the next npm release. Once `openclaw@2026.2.15` is published, publish this advisory without further edits.

Thanks @xuemian168 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p536-vvpp-9mc8
- https://github.com/openclaw/openclaw/commit/166cf6a3e04c7df42bea70a7ad5ce2b9df46d147
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
