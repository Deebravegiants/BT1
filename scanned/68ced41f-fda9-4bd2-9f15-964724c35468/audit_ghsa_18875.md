# [H] Zitadel May Bypass Second Authentication Factor

## Summary
Severity: High
Advisory: GHSA-cfjq-28r2-4jv5
CVE: CVE-2025-64103
CWE: CWE-287, CWE-308
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-cfjq-28r2-4jv5
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.53.6
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.54.3
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.55.0 <2.71.18
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20251029091250-b284f8474eed

## Details
### Summary

A vulnerability in Zitadel's token verification prematurely marked sessions as authenticated when only one factor was verified. 

### Impact

Zitadel provides an API for managing sessions, enabling custom login experiences in a dedicated UI or direct integration into applications. Session Tokens are issued for active sessions, which can be used as Bearer tokens to call the Zitadel API.

Starting from 2.55.0 (see other affected versions below), Zitadel only required multi factor authentication in case the login policy has either enabled `requireMFA` or `requireMFAForLocalUsers`. If a user has set up MFA without this requirement, Zitadel would consider single factor auhtenticated sessions as valid as well and not require multiple factors.

Bypassing second authentication factors weakens multifactor authentication and enables attackers to bypass the more secure factor. An attacker can target the TOTP code alone, only six digits, bypassing password verification entirely and potentially compromising accounts with 2FA enabled.

### Affected Versions

Systems using the session API (v2 beta and v2) directly or via the new login UI in the following versions are affected:
- **4.x**: `4.0.0` to `4.5.0` (including RC versions)
- **3.x**: `3.0.0` to `3.4.2` (including RC versions)
- **2.x**: `v2.53.6` to `v2.53.9`,  `v2.54.3` to `v2.54.10`, `2.55.0` to `2.71.17`

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by requiring a configured second factor regardless of the login policies `requireMFA` or `requireMFAForLocalUsers` configuration.

4.x: Upgrade to >=[4.6.0](https://github.com/zitadel/zitadel/releases/tag/v4.6.0)
3.x: Update to >=[3.4.3](https://github.com/zitadel/zitadel/releases/tag/v3.4.3)
2.x: Update to >=[2.71.18](https://github.com/zitadel/zitadel/releases/tag/v2.71.18)

### Workarounds

The recommended solution is to update Zitadel to a patched version.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

This vulnerability was found by [zentrust partners GmbH](https://zentrust.partners) during a scheduled penetration test. Thank you to the analysts Martin Tschirsich, Joud Zakharia, Christopher Baumann.
The full report will be made public after the complete review.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-cfjq-28r2-4jv5
- https://nvd.nist.gov/vuln/detail/CVE-2025-64103
- https://github.com/zitadel/zitadel/commit/b284f8474eed0cba531905101619e7ae7963156b
- https://github.com/zitadel/zitadel
- https://pkg.go.dev/vuln/GO-2025-4083
