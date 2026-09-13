# [M] OpenClaw affected by Stored XSS in Control UI via unsanitized assistant name/avatar in inline script injection

## Summary
Severity: Medium
Advisory: GHSA-37gc-85xm-2ww6
CVE: CVE-2026-27009
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-37gc-85xm-2ww6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Summary
Stored XSS in the OpenClaw Control UI when rendering assistant identity (name/avatar) into an inline `<script>` tag without script-context-safe escaping. A crafted value containing `</script>` could break out of the script tag and execute attacker-controlled JavaScript in the Control UI origin.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.14`
- Fixed in: `>= 2026.2.15` (next release; fix is already merged on `main`)

## Details
The gateway Control UI HTML response previously injected `assistantName` and `assistantAvatar` directly into an inline `<script>` block using `JSON.stringify(...)`. `JSON.stringify` does not prevent `</script>` from terminating the script element, enabling stored XSS if an operator/admin sets the assistant identity to a malicious string.

OpenClaw’s Control UI is intended for local use only (see `SECURITY.md`); this advisory’s CVSS reflects a loopback-only/local-access deployment assumption.

## Impact
An attacker with the ability to set assistant identity values (config or agent identity) could cause JavaScript execution for Control UI visitors, enabling token/session theft and privileged actions in the UI.

## Fix
- Removed inline script injection and serve bootstrap config from a JSON endpoint.
- Added a restrictive Content Security Policy for the Control UI (`script-src 'self'`, no inline scripts).

## Fix Commit(s)
- `adc818db4a4b3b8d663e7674ef20436947514e1b`
- `3b4096e02e7e335f99f5986ec1bd566e90b14a7e`

## Release Process Note
This advisory pre-sets the patched version to the planned next release (`2026.2.15`). Once that version is published to npm, this advisory can be published without further edits.

Thanks @Adam55A-code for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-37gc-85xm-2ww6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27009
- https://github.com/openclaw/openclaw/commit/3b4096e02e7e335f99f5986ec1bd566e90b14a7e
- https://github.com/openclaw/openclaw/commit/adc818db4a4b3b8d663e7674ef20436947514e1b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
