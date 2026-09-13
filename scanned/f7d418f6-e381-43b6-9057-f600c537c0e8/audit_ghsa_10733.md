# [M] OpenClaw: OpenShell mirror mode could delete arbitrary remote directories when roots were mis-scoped

## Summary
Severity: Medium
Advisory: GHSA-m34q-h93w-vg5x
CVE: CVE-2026-41383
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-m34q-h93w-vg5x
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, the OpenShell mirror backend accepted arbitrary absolute `remoteWorkspaceDir` and `remoteAgentWorkspaceDir` values. In mirror mode, those paths were then used as the target of remote cleanup and overwrite operations.

## Impact

If an attacker could influence those OpenShell config values, mirror sync could delete the contents of an unintended remote directory and replace them with uploaded workspace data. This was a destructive remote-path bug in the mirror-sync path.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `b21c9840c2e38f4bb338d031511b479d5f07ca25` — constrain OpenShell mirror sync roots

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @jufeng123768 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m34q-h93w-vg5x
- https://github.com/openclaw/openclaw/commit/b21c9840c2e38f4bb338d031511b479d5f07ca25
- https://github.com/openclaw/openclaw
