# [H] ALPINE-CVE-2023-1999

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-1999
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-1999
Type: osv

## Affected
- Alpine:v3.15: `libwebp` — affected >=0.4.2 <1.2.2-r1
- Alpine:v3.16: `libwebp` — affected >=0.4.2 <1.2.3-r1
- Alpine:v3.17: `libwebp` — affected >=0.4.2 <1.2.4-r2
- Alpine:v3.18: `libwebp` — affected >=0.4.2 <1.3.0-r2
- Alpine:v3.19: `libwebp` — affected >=0.4.2 <1.3.0-r3
- Alpine:v3.20: `libwebp` — affected >=0.4.2 <1.3.0-r3
- Alpine:v3.21: `libwebp` — affected >=0.4.2 <1.3.0-r3
- Alpine:v3.22: `libwebp` — affected >=0.4.2 <1.3.0-r3
- Alpine:v3.23: `libwebp` — affected >=0.4.2 <1.3.0-r3
- Alpine:v3.24: `libwebp` — affected >=0.4.2 <1.3.0-r3

## Details
There exists a use after free/double free in libwebp. An attacker can use the ApplyFiltersAndEncode() function and loop through to free best.bw and assign best = trial pointer. The second loop will then return 0 because of an Out of memory error in VP8 encoder, the pointer is still assigned to trial and the AddressSanitizer will attempt a double free.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-1999
