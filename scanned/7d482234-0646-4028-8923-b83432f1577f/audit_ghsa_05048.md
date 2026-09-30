# [H] Kahi has privilege-drop and socket/log permission issues

## Summary
Severity: High
Advisory: GHSA-55f6-4pr5-c7m5
CWE: CWE-271, CWE-732
Ecosystem: Go
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-55f6-4pr5-c7m5
Type: github-advisory

## Affected
- Go: `github.com/kahiteam/kahi` — affected >=0 <0.1.0-alpha.9

## Details
Kahi releases up to and including v0.1.0-alpha.8 contain three privilege/permission issues, all fixed in v0.1.0-alpha.9. They were identified in a full-codebase security review on 2026-05-26.

## Affected versions
All releases <= v0.1.0-alpha.8.

## Patched version
v0.1.0-alpha.9.

## Details

### 1. Per-process privilege drop not applied (High)
A process configured with `user = "uid:gid"` had its credential resolved but never attached to the spawned child, so the process ran with the supervisor's inherited privileges (root, when the supervisor runs as root) instead of the configured lower-privilege user. The intended privilege isolation did not occur, and no error was raised.

### 2. Privilege drop did not reset supplementary groups (Medium)
When the daemon dropped privileges it set the primary gid and uid but never called setgroups(2), so the launching user's supplementary groups (for example `docker`, which is root-equivalent) remained active after the drop and were inherited by child processes.

### 3. FastCGI unix socket world-accessible by default (Medium)
A FastCGI unix-domain socket was chmod-ed only when `socket_mode` was explicitly configured. With `socket_mode` unset the socket kept the umask-dependent default (commonly world-accessible), allowing any local user to connect to it.

## Remediation
Upgrade to v0.1.0-alpha.9. Privilege handling is now fail-closed: the configured credential is applied or the process refuses to start, supplementary groups are reset via setgroups before setgid/setuid, and FastCGI unix sockets default to 0700.

## Workarounds (for <= v0.1.0-alpha.8)
- Do not rely on per-process `user`; run the supervisor directly as the intended unprivileged user.
- Set an explicit restrictive `socket_mode` on FastCGI programs.
- Avoid running the supervisor as root where possible.

## References
- https://github.com/kahiteam/kahi/security/advisories/GHSA-55f6-4pr5-c7m5
- https://github.com/kahiteam/kahi
