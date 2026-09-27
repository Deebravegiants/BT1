# [M] ALPINE-CVE-2025-26466

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-26466
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-26466
Type: osv

## Affected
- Alpine:v3.19: `openssh` — affected >=0 <9.6_p1-r2
- Alpine:v3.20: `openssh` — affected >=0 <9.7_p1-r5
- Alpine:v3.21: `openssh` — affected >=0 <9.9_p2-r0
- Alpine:v3.22: `openssh` — affected >=0 <9.9_p2-r0
- Alpine:v3.23: `openssh` — affected >=0 <9.9_p2-r0
- Alpine:v3.24: `openssh` — affected >=0 <9.9_p2-r0

## Details
A flaw was found in the OpenSSH package. For each ping packet the SSH server receives, a pong packet is allocated in a memory buffer and stored in a queue of packages. It is only freed when the server/client key exchange has finished. A malicious client may keep sending such packages, leading to an uncontrolled increase in memory consumption on the server side. Consequently, the server may become unavailable, resulting in a denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-26466
