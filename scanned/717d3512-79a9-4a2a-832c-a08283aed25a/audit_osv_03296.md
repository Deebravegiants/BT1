# [M] ALPINE-CVE-2025-47203

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-47203
Ecosystem: Alpine:v3.24
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47203
Type: osv

## Affected
- Alpine:v3.24: `dropbear` — affected >=0 <2025.88-r0

## Details
dbclient in Dropbear SSH before 2025.88 allows command injection via an untrusted hostname argument, because a shell is used.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47203
