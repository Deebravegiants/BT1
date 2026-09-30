# [C] ALPINE-CVE-2024-12084

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-12084
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12084
Type: osv

## Affected
- Alpine:v3.18: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.19: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.20: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.0-r0

## Details
A heap-based buffer overflow flaw was found in the rsync daemon. This issue is due to improper handling of attacker-controlled checksum lengths (s2length) in the code. When MAX_DIGEST_LEN exceeds the fixed SUM_LENGTH (16 bytes), an attacker can write out of bounds in the sum2 buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12084
