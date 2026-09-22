# [H] ALPINE-CVE-2026-78408

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-78408
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-78408
Type: osv

## Affected
- Alpine:v3.22: `util-linux` — affected >=0 <2.41.6-r1
- Alpine:v3.23: `util-linux` — affected >=0 <2.41.6-r1
- Alpine:v3.24: `util-linux` — affected >=0 <2.42.3-r1

## Details
The nsenter --join-cgroup option opens the target cgroup.procs file as root and leaves that file descriptor open across later namespace and credential changes and across execve(). Because the kernel checks later cgroup migrations using the credentials from the original open, a program run in an attacker-controlled target can inherit root's ability to move host processes between cgroups. After a privileged operator uses --join-cgroup against that target, an unprivileged user can migrate and terminate unrelated root processes.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-78408
