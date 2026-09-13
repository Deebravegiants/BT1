# [H] Coder vulnerable to OIDC account takeover via email-based user matching and email_verified bypass

## Summary
Severity: High
Advisory: GHSA-9r87-mvcw-x35f
CVE: CVE-2026-55075
CWE: CWE-287, CWE-289
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-9r87-mvcw-x35f
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

Two flaws in Coder's OIDC login chained into account takeover: email-based user matching fell back to linking by email without checking for an existing link to a different IdP subject and the `email_verified` claim was only enforced when present as a boolean `false` so an absent or non-boolean claim was treated as verified.

### Impact

An attacker who could authenticate at the configured OIDC provider with an email matching a victim's Coder account could log in as that victim and gain full access to their workspaces, templates and resources. This required OIDC authentication, attacker control of a matching email at the IdP and a victim account not yet linked to a different IdP subject.

### Patches

The fix restricts the email fallback to first-time and legacy linking and defaults `email_verified` to false when the claim is absent or of an unexpected type.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Configure the OIDC provider to disallow self-registration or to require email verification before issuing tokens.

### Resources

- Fix: #25712, #25713

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22450) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-9r87-mvcw-x35f
- https://github.com/coder/coder/pull/25712
- https://github.com/coder/coder/pull/25713
- https://github.com/coder/coder
