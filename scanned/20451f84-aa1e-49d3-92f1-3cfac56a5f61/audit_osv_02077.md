# [C] ALPINE-CVE-2021-20314

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-20314
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20314
Type: osv

## Affected
- Alpine:v3.11: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.12: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.13: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.14: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.15: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.16: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.17: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.18: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.19: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.20: `libspf2` — affected >=0 <1.2.10-r5
- Alpine:v3.21: `libspf2` — affected >=0 <1.2.11-r4
- Alpine:v3.22: `libspf2` — affected >=0 <1.2.11-r4
- Alpine:v3.23: `libspf2` — affected >=0 <1.2.11-r4
- Alpine:v3.24: `libspf2` — affected >=0 <1.2.11-r4

## Details
Stack buffer overflow in libspf2 versions below 1.2.11 when processing certain SPF macros can lead to Denial of service and potentially code execution via malicious crafted SPF explanation messages.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20314
