# [H] Coder vulnerable to SSH config injection via unsanitized server-supplied values in `coder config-ssh`

## Summary
Severity: High
Advisory: GHSA-mcqq-fqgf-rxwm
CVE: CVE-2026-55427
CWE: CWE-74, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-mcqq-fqgf-rxwm
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

`coder config-ssh` wrote server-supplied SSH settings (`HostnameSuffix`, `SSHConfigOptions`) into the user's `~/.ssh/config` without sanitizing embedded newlines or restricting directives so a malicious or compromised Coder server could inject arbitrary SSH configuration.

> **Note:** Practical exploitation requires control of the server-supplied values through a malicious or compromised deployment, a man-in-the-middle position or admin access to the `HostnameSuffix` and `SSHConfigOptions` settings.

### Impact

A server administrator or an attacker who controlled the server, could inject a directive such as `ProxyCommand` and achieve arbitrary code execution on any developer workstation that ran `coder config-ssh`. Injected commands ran with the local user's privileges and applied to all SSH connections, not just Coder workspaces.

### Patches

The fix validates `HostnameSuffix` and `SSHConfigOptions` against a strict character set that rejects newlines and other control characters.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Inspect `coder config-ssh --dry-run` output before applying changes.

### Resources

- Fix: #26154

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22437) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-mcqq-fqgf-rxwm
- https://github.com/coder/coder/pull/26154
- https://github.com/coder/coder
