# [M] Coder's sub-agent app registration bypasses template port-sharing policy enforcement

## Summary
Severity: Medium
Advisory: GHSA-x9qq-2qh5-8rxf
CVE: CVE-2026-55432
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-x9qq-2qh5-8rxf
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The `CreateSubAgent` RPC did not validate a requested app sharing level against the template's `MaxPortSharingLevel` before persisting workspace apps, letting a workspace owner exceed the administrator's configured maximum.

> **Note:** Exploitation requires the ability to register sub-agent apps in a workspace the attacker controls.

### Impact

A workspace owner with an agent token could register a sub-agent app as `PUBLIC` even when the template's `MaxPortSharingLevel` was `owner`, exposing the app to unauthenticated users via the wildcard app domain. This affected only deployments using Enterprise port-sharing policy and wildcard app hostnames and required an authenticated workspace owner with an agent token.

### Patches

The fix clamps the sub-agent app sharing level to the template's `MaxPortSharingLevel`.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Disable wildcard app hostnames (`CODER_WILDCARD_ACCESS_URL`) to block subdomain-based app routing.

### Resources

- Fix: #26061

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22452) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-x9qq-2qh5-8rxf
- https://github.com/coder/coder/pull/26061
- https://github.com/coder/coder
