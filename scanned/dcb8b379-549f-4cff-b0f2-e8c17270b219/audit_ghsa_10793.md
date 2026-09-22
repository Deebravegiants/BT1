# [M] OpenClaw: Pairing pending-request caps were enforced per channel instead of per account

## Summary
Severity: Medium
Advisory: GHSA-wwfp-w96m-c6x8
CVE: CVE-2026-41346
CWE: CWE-799
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-wwfp-w96m-c6x8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.26 <2026.3.31

## Details
## Summary

Before OpenClaw 2026.3.31, pending pairing-request caps were enforced per channel file instead of per account. On multi-account channel setups, requests from other accounts could fill the shared pending window and block new pairing challenges on an unaffected account.

## Impact

This issue could deny new pairing or onboarding on another account until an existing request was approved or expired. It was an availability-only bug; it did not allow cross-account approval, data access, or authorization bypass.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `>= 2026.2.26, < 2026.3.31`
- Patched versions: `>= 2026.3.31`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `9bc1f896c8cd325dd4761681e9bdb8c425f69785` — scope pending request caps per account

## Release Process Note

The fix shipped in OpenClaw `2026.3.31` on March 31, 2026. The current published npm release `2026.4.1` from April 1, 2026 also contains the fix.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wwfp-w96m-c6x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41346
- https://github.com/openclaw/openclaw/commit/9bc1f896c8cd325dd4761681e9bdb8c425f69785
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-improper-pending-pairing-request-cap-enforcement
