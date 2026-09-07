# [H] OpenClaw: Linux and macOS exec allowlists skipped configured argument patterns

## Summary
Severity: High
Advisory: GHSA-v2ww-5rh7-2h5v
CVE: CVE-2026-53853
CWE: CWE-693, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-v2ww-5rh7-2h5v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

OpenClaw's exec allowlist supported optional `argPattern` entries to restrict the arguments accepted for an allowlisted executable. In affected releases, Linux and macOS gateways skipped `argPattern` checks and treated a matching executable path as sufficient to satisfy the allowlist.

This meant an operator could configure an allowlist entry that appeared to permit only a narrow argv shape, but OpenClaw would allow other argv for the same executable without an approval prompt when `tools.exec.security` was set to `allowlist`.

This issue is limited to direct enforcement of configured `argPattern` values. OpenClaw's exec approvals remain best-effort guardrails and do not attempt to semantically model every interpreter, loader, package script, shell feature, or transitive file a command may use.

### Affected configurations

This affects OpenClaw gateway deployments that meet all of these conditions:

- the gateway runs on Linux or macOS
- exec is configured with `tools.exec.security: "allowlist"`
- at least one exec allowlist entry uses `argPattern`
- the allowlisted executable accepts security-relevant arguments or flags

Path-only allowlist entries are not additionally affected by this issue, because those entries intentionally allow any arguments for the matched executable. Windows was not affected by this specific bug because the affected code path already applied `argPattern` checks on Windows.

### Impact

If an untrusted or lower-trust sender can influence a tool-enabled agent to call exec, they may be able to run disallowed arguments for an executable that the operator intended to restrict with `argPattern`. Depending on the executable, those arguments can cause host-side file access, network access, or command execution that should have required an approval prompt.

The practical impact depends on the operator's allowlist and channel exposure. Examples of higher-risk allowlisted executables include tools with interpreter, loader, subprocess, network, or plugin flags such as `git`, `python`, `node`, `bash`, `find`, `tar`, and `ssh`.

This is not a bypass of all exec approval semantics. It is a bypass of the direct `argPattern` predicate that the operator configured and that the exec tool description advertised as enforced at runtime.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

Upgrade to `openclaw@2026.5.12` or later. Before upgrading, operators who use exec allowlist mode should review entries that combine an executable path with `argPattern`, especially for interpreter-like or subprocess-capable tools.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v2ww-5rh7-2h5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-53853
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-argument-pattern-bypass-in-exec-allowlist-via-linux-and-macos
