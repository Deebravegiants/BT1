# [M] ALPINE-CVE-2025-10158

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-10158
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-10158
Type: osv

## Affected
- Alpine:v3.19: `rsync` — affected >=0 <3.4.1-r1
- Alpine:v3.20: `rsync` — affected >=0 <3.4.1-r1
- Alpine:v3.21: `rsync` — affected >=0 <3.4.1-r1
- Alpine:v3.22: `rsync` — affected >=0 <3.4.1-r1
- Alpine:v3.23: `rsync` — affected >=0 <3.4.1-r1
- Alpine:v3.24: `rsync` — affected >=0 <3.4.1-r1

## Details
A malicious client acting as the receiver of an rsync file transfer can trigger an out of bounds read of a heap based buffer, via a negative array index. The 

malicious 

rsync client requires at least read access to the remote rsync module in order to trigger the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-10158
