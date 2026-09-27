# [H] ZITADEL Vulnerable to Account Takeover Due to Improper Instance Validation in V2 Login

## Summary
Severity: High
Advisory: GHSA-pfrf-9r5f-73f5
CVE: CVE-2026-29067
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-pfrf-9r5f-73f5
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20251208091519-4c879b47334e
- Go: `github.com/zitadel/zitadel` — affected >=1.83.4
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0-rc.1 <4.7.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=0 <1.80.0-v2.20.0.20251208091519-4c879b47334e

## Details
### Summary

A potential vulnerability exists in ZITADEL's password reset mechanism in login V2. ZITADEL utilizes the Forwarded or X-Forwarded-Host header from incoming requests to construct the URL for the password reset confirmation link. This link, containing a secret code, is then emailed to the user.

### Impact

If an attacker can manipulate these headers (e.g., via host header injection), they could cause ZITADEL to generate a password reset link pointing to a malicious domain controlled by the attacker. If the user clicks this manipulated link in the email, the secret reset code embedded in the URL can be captured by the attacker. This captured code could then be used to reset the user's password and gain unauthorized access to their account.

It's important to note that this specific attack vector is mitigated for accounts that have Multi-Factor Authentication (MFA) or Passwordless authentication enabled.

### Affected Versions

Systems using the login UI (v2) and running one of the following versions are affected:
- **v4.x**: `4.0.0-rc.1` through `4.7.0`

### Patches

The vulnerability has been addressed in the latest release. The patch resolves the issue by correctly validating the X-Forwarded-Host and Forwarded headers against the instance custom and trusted domains.

Before you upgrade, ensure that:
- the `ZITADEL_API_URL` is set and is pointing to your instance, resp. system in multi-instance deployments.
- the HTTP `host` (or a `x-forwarded-host`) is passed in your reverse proxy to the login UI.
- a `x-zitadel-instance-host` (or `x-zitadel-forward-host`) is set in your reverse for multi-instance deployments. If you're running a single instance solution, you don't need to take any actions.

Patched versions:
- 4.x: Upgrade to >=[4.7.1](https://github.com/zitadel/zitadel/releases/tag/v4.7.1)

### Workarounds

The recommended solution is to update ZITADEL to a patched version.

A ZITADEL fronting proxy can be configured to delete all forwarded header values or set it to the requested host before sending requests to ZITADEL self-hosted environments.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Amit Laish – GE Vernova for finding and reporting the vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-pfrf-9r5f-73f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-29067
- https://github.com/zitadel/zitadel/commit/4c879b47334e01d4fcab921ac1b44eda39acdb96
- https://github.com/zitadel/zitadel
