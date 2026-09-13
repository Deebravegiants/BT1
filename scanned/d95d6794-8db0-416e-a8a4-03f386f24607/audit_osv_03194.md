# [M] ALPINE-CVE-2025-14282

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14282
Ecosystem: Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14282
Type: osv

## Affected
- Alpine:v3.24: `dropbear` — affected >=0 <2025.89-r0

## Details
A flaw was found in Dropbear. When running in multi-user mode and authenticating users, the dropbear ssh server does the socket forwardings requested by the remote client as root,
only switching to the logged-in user upon spawning a shell or performing
some operations like reading the user's files.
With the recent ability of also using unix domain sockets as the forwarding destination any user able to log in via ssh can connect to any unix socket with the root's credentials, bypassing both file system restrictions and any SO_PEERCRED / SO_PASSCRED checks performed by the peer.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14282
