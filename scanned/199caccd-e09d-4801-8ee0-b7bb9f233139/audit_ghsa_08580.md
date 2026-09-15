# [M] nono: Sandbox escape on Linux via D-Bus: `systemd-run --user`

## Summary
Severity: Medium
Advisory: GHSA-27vp-2mmc-vmh3
CVE: CVE-2026-47128
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-27vp-2mmc-vmh3
Type: github-advisory

## Affected
- crates.io: `nono-cli` — affected >=0 <0.55.0

## Details
### Summary

The nono Landlock/seccomp policies allow access to local Unix domain sockets (concrete and abstract). This allows an easy sandbox escape by talking to the per-user systemd dbus socket.

Threat scenario: Running Aider, Claude Code, OpenCode or similar tools with "allow bash" policy so that it can invoke arbitrary host tools like `make`, `gcc`, etc. to write code.

### Reproducer

Here, instead of running a tool like `opencode` or `claude` one can just invoke `systemd-run`, but this is something an agent could be tricked into doing:

```bash
$ cd ~/src/myproject
$ nono run -s --allow-cwd --profile claude-code -- \
      systemd-run --user -q --wait --collect \
      /bin/sh -c "echo oops > ~/Documents/escaped.txt"
$ cat /var/home/test/Documents/escaped.txt
oops
$
```

### Impact

Complete sandbox escape. The unsandboxed sibling process can write anywhere the user can write, spawn arbitrary processes with network access, etc.

### Maintainer Context

This issue allows a process running inside the sandbox to escape confinement by interacting with local user-scoped IPC mechanisms and regain the authority already held by the invoking user or service account.

The issue impacts the sandbox’s confinement and blast-radius reduction guarantees for agents and sandboxed tooling. However, exploitation does not provide privilege escalation, cross-user access, or host compromise beyond the permissions already available to the launcher outside the sandbox.

This issue affects the CLI policy layer and bundled sandbox profiles. The underlying core library `nono` does not ship with policy definitions or agent-facing confinement profiles by default, nor do the language SDKs.

This is considered a serious issue because an AI agent or untrusted command stream operating within the sandbox could abuse the bypass to perform unauthorized or destructive actions using the delegated authority of the launching user.

The root cause was incomplete mediation of local Unix domain socket access within affected sandbox policies. Support for restricting this behavior has since been added and the fix is available in the repository pending release.

CVSS rationale: exploitation requires execution within a locally launched sandboxed process using the authority already delegated by the invoking user or service account (`AV:L/PR:L`). The issue allows reliable bypass of sandbox confinement and policy guarantees, resulting in high integrity impact (`I:H`) and limited availability impact (`A:L`) through destructive actions within the launcher’s existing permissions. However, the issue does not provide privilege escalation, cross-user access, or a change in security scope (`S:U`).

## References
- https://github.com/always-further/nono/security/advisories/GHSA-27vp-2mmc-vmh3
- https://github.com/always-further/nono
