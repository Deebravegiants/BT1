# [M] ALPINE-CVE-2025-47268

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-47268
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47268
Type: osv

## Affected
- Alpine:v3.23: `iputils` — affected >=0 <20250602-r0
- Alpine:v3.24: `iputils` — affected >=0 <20250602-r0

## Details
ping in iputils before 20250602 allows a denial of service (application error or incorrect data collection) via a crafted ICMP Echo Reply packet, because of a signed 64-bit integer overflow in timestamp multiplication.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47268
