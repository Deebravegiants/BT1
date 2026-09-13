# [H] ALPINE-CVE-2026-41054

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41054
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41054
Type: osv

## Affected
- Alpine:v3.20: `haveged` — affected >=0 <1.9.21-r0
- Alpine:v3.21: `haveged` — affected >=0 <1.9.21-r0
- Alpine:v3.22: `haveged` — affected >=0 <1.9.21-r0
- Alpine:v3.23: `haveged` — affected >=0 <1.9.21-r0
- Alpine:v3.24: `haveged` — affected >=0 <1.9.21-r0

## Details
In `src/havegecmd.c`, the `socket_handler` function performs a credential check on the abstract UNIX socket (`\0/sys/entropy/haveged`). However, while it detects if the connecting user is not root (`cred.uid != 0`) and prepares a negative acknowledgement (`ASCII_NAK`), it **fails to stop execution**. The code proceeds to the `switch` statement, allowing any local unprivileged user to execute privileged commands such as `MAGIC_CHROOT`.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41054
