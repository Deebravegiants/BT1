# [M] ALPINE-CVE-2020-29568

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29568
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29568
Type: osv

## Affected
- Alpine:v3.13: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.14: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.15: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.16: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.17: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.18: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.19: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.20: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.21: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.22: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.23: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.24: `linux-lts` — affected >=0 <5.10.4-r0

## Details
An issue was discovered in Xen through 4.14.x. Some OSes (such as Linux, FreeBSD, and NetBSD) are processing watch events using a single thread. If the events are received faster than the thread is able to handle, they will get queued. As the queue is unbounded, a guest may be able to trigger an OOM in the backend. All systems with a FreeBSD, Linux, or NetBSD (any version) dom0 are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29568
