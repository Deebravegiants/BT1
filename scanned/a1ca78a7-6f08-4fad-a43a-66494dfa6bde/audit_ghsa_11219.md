# [C] OpenBao has Reflected XSS in its OIDC authentication error message

## Summary
Severity: Critical
Advisory: GHSA-cpj3-3r2f-xj59
CVE: CVE-2026-33758
CWE: CWE-20, CWE-80
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cpj3-3r2f-xj59
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20260325133417-6e2b2dd84f0e

## Details
### Impact

OpenBao installations that have an OIDC/JWT authentication method enabled and a role with `callback_mode=direct` configured are vulnerable to XSS via the  `error_description` parameter on the page for a failed authentication.

This allows an attacker access to the token used in the Web UI by a victim.

### Patches
The `error_description` parameter has been replaced with a static error message in v2.5.2

### Workarounds
The vulnerability can be mitigated by removing any roles with `callback_mode` set to `direct`.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-cpj3-3r2f-xj59
- https://nvd.nist.gov/vuln/detail/CVE-2026-33758
- https://github.com/openbao/openbao/pull/2709
- https://github.com/openbao/openbao/commit/6e2b2dd84f0e47cebc90d6e79609dd5274732662
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.2
