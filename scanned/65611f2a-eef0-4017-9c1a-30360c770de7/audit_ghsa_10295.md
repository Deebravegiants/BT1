# [M] OpenClaw: Android accepted cleartext remote gateway endpoints and sent stored credentials over ws://

## Summary
Severity: Medium
Advisory: GHSA-83f3-hh45-vfw9
CVE: CVE-2026-40045
CWE: CWE-200, CWE-319
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-83f3-hh45-vfw9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, Android accepted non-loopback cleartext `ws://` gateway endpoints and would send stored gateway credentials over that connection. Discovery beacons or setup codes could therefore steer the client onto a cleartext remote endpoint.

## Impact

A user who followed a forged discovery result or scanned a crafted setup code could disclose stored gateway credentials to an attacker-controlled endpoint in plaintext. This was a transport-security bug in the Android gateway client.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `a941a4fef9bc43b2973c92d0dcff5b8a426210c5` — require TLS for remote Android gateway endpoints

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-83f3-hh45-vfw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40045
- https://github.com/openclaw/openclaw/commit/a941a4fef9bc43b2973c92d0dcff5b8a426210c5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-cleartext-credential-transmission-via-unencrypted-websocket-gateway-endpoints
