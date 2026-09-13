# [H] sh _uid does not drop supplementary groups (incomplete privilege drop)

## Summary
Severity: High
Advisory: GHSA-q38v-wp89-2w55
CVE: CVE-2026-54552
CWE: CWE-273
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-q38v-wp89-2w55
Type: github-advisory

## Affected
- PyPI: `sh` — affected >=0 <2.2.4

## Details
### Impact
The `_uid` option performed an incomplete privilege drop on Linux/Unix-like systems.

When `sh` was run from a process with elevated privileges, such as root, and a command was launched with `_uid=<unprivileged user>`, the child process changed its UID and primary GID but did not reset its supplementary groups. As a result, the child process could retain the parent process’s supplementary groups, potentially including privileged groups such as root, docker, disk, shadow, or sudo.

This could allow a subprocess that was expected to run with reduced privileges to access files or resources available to the original process’s supplementary groups. Users are impacted if they rely on `_uid` as a privilege boundary when launching commands from a privileged parent process.

### Patches
Upgrade to version >= 2.2.4

### Workarounds
Avoid using `_uid` when the user represents a less-privileged user.

## References
- https://github.com/amoffat/sh/security/advisories/GHSA-q38v-wp89-2w55
- https://github.com/amoffat/sh
- https://github.com/amoffat/sh/releases/tag/2.2.4
