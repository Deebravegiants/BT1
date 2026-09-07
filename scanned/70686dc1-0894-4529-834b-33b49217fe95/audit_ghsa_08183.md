# [H] OpenClaw/Clawdbot has OS Command Injection via Project Root Path in sshNodeCommand

## Summary
Severity: High
Advisory: GHSA-q284-4pvr-m585
CVE: CVE-2026-25157
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-q284-4pvr-m585
Type: github-advisory

## Affected
- npm: `clawdbot` — affected >=0 <2026.1.29

## Details
Two related vulnerabilities existed in the macOS application's SSH remote connection handling (`CommandResolver.swift`):

## Details

The `sshNodeCommand` function constructed a shell script without properly escaping the user-supplied project path in an error message. When the `cd` command failed, the unescaped path was interpolated directly into an `echo` statement, allowing arbitrary command execution **on the remote SSH host**.

The `parseSSHTarget` function did not validate that SSH target strings could not begin with a dash. An attacker-supplied target like `-oProxyCommand=...` would be interpreted as an SSH configuration flag rather than a hostname, allowing arbitrary command execution **on the local machine**.

## Impact

An attacker who can influence a user's remote connection settings (via social engineering or malicious configuration) could achieve arbitrary code execution on either the user's local machine or their configured remote SSH host, depending on which input vector is exploited.

**Affected component:** macOS menubar application (Remote/SSH mode only)

**Not affected:** CLI (`npm install openclaw`), web gateway, iOS/Android apps, or users running in Local mode.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q284-4pvr-m585
- https://nvd.nist.gov/vuln/detail/CVE-2026-25157
- https://github.com/openclaw/openclaw
