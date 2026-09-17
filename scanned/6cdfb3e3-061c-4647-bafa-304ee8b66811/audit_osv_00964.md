# [H] ALPINE-CVE-2018-13139

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-13139
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-13139
Type: osv

## Affected
- Alpine:v3.10: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.11: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.12: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.13: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.14: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.15: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.16: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.17: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.18: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.19: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.20: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.21: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.22: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.23: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.24: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.5: `libsndfile` — affected >=0 <1.0.28-r3
- Alpine:v3.6: `libsndfile` — affected >=0 <1.0.28-r3
- Alpine:v3.7: `libsndfile` — affected >=0 <1.0.28-r3
- Alpine:v3.8: `libsndfile` — affected >=0 <1.0.28-r4
- Alpine:v3.9: `libsndfile` — affected >=0 <1.0.28-r4

## Details
A stack-based buffer overflow in psf_memset in common.c in libsndfile 1.0.28 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted audio file. The vulnerability can be triggered by the executable sndfile-deinterleave.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-13139
