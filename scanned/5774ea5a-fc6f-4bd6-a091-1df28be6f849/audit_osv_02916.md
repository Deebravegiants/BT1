# [H] ALPINE-CVE-2023-4863

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-4863
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4863
Type: osv

## Affected
- Alpine:v3.15: `libwebp` — affected >=0 <1.2.2-r2
- Alpine:v3.16: `libwebp` — affected >=0 <1.2.3-r2
- Alpine:v3.17: `libwebp` — affected >=0 <1.2.4-r3
- Alpine:v3.18: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.19: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.20: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.21: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.22: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.23: `libwebp` — affected >=0 <1.3.1-r1
- Alpine:v3.24: `libwebp` — affected >=0 <1.3.1-r1

## Details
Heap buffer overflow in libwebp in Google Chrome prior to 116.0.5845.187 and libwebp 1.3.2 allowed a remote attacker to perform an out of bounds memory write via a crafted HTML page. (Chromium security severity: Critical)

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4863
