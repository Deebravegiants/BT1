# [H] ALPINE-CVE-2026-41035

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41035
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41035
Type: osv

## Affected
- Alpine:v3.20: `rsync` — affected >=3.0.1 <3.4.1-r2
- Alpine:v3.21: `rsync` — affected >=3.0.1 <3.4.1-r2
- Alpine:v3.22: `rsync` — affected >=3.0.1 <3.4.1-r2
- Alpine:v3.23: `rsync` — affected >=3.0.1 <3.4.1-r2
- Alpine:v3.24: `rsync` — affected >=3.0.1 <3.4.1-r2

## Details
In rsync 3.0.1 through 3.4.1, receive_xattr relies on an untrusted length value during a qsort call, leading to a receiver use-after-free. The victim must run rsync with -X (aka --xattrs). On Linux, many (but not all) common configurations are vulnerable. Non-Linux platforms are more widely vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41035
