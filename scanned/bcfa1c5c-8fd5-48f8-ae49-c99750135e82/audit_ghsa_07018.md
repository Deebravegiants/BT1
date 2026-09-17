# [H] Coder: User-admin role can reset owner account password

## Summary
Severity: High
Advisory: GHSA-29xf-69gq-m9jx
CVE: CVE-2026-55077
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-29xf-69gq-m9jx
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The `PUT /api/v2/users/{user}/password` endpoint authorized only `ActionUpdatePersonal` and did not prevent a `user-admin` from resetting an `owner` account's password. It also did not require the current password when an admin reset another user's password.

> **Note:** Exploitation requires the privileged `user-admin` role so practical risk is limited to deployments that grant `user-admin` to less trusted operators.

### Impact

A `user-admin` could reset any owner's password without knowing it, authenticate as that owner and gain full deployment control, including templates, workspaces, licensing, organization settings and the ability to self-assign the `owner` role. This was a privilege escalation from `user-admin` to `owner`.

### Patches

The fix prevents non-owner users from resetting the password of an account that holds the `owner` role.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Restrict the `user-admin` role to trusted administrators until upgrading.

### Resources
- Fix: #25709

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22436) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-29xf-69gq-m9jx
- https://github.com/coder/coder/pull/25709
- https://github.com/coder/coder
