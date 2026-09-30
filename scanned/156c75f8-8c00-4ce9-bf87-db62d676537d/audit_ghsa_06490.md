# [H] Coder's OIDC email_verified type coercion bypass enables account takeover via unverified email linking

## Summary
Severity: High
Advisory: GHSA-75vm-6w67-gwvp
CVE: CVE-2026-55076
CWE: CWE-287, CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-75vm-6w67-gwvp
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

Coder's OIDC callback checked `email_verified` with a direct Go `bool` type assertion. When an IdP returned the claim as a non-boolean (for example the string `"false"`) or omitted it, the assertion failed open and the email was treated as verified. Combined with an unconditional email-based account fallback, this enabled account takeover.

### Impact

An attacker who registered a victim's email at a compatible IdP without verifying it could log in via OIDC and be matched to the victim's existing Coder account, receiving a session for that account. No prior authentication to Coder was required and the result was full account takeover.

### Patches

The fix coerces `email_verified` across bool, string and numeric types (fail-closed) and blocks the email fallback when the matched user already has a different linked IdP subject.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Ensure the IdP returns `email_verified` as a native JSON boolean. The email-fallback linking issue has no configuration workaround; upgrading is required.

### Resources

- Fix: #25712, #25713

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22444) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-75vm-6w67-gwvp
- https://github.com/coder/coder
