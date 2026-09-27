# [M] ALPINE-CVE-2017-7585

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7585
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7585
Type: osv

## Affected
- Alpine:v3.10: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.11: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.12: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.13: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.14: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.15: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.16: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.17: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.18: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.19: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.2: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.20: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.21: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.22: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.23: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.24: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.3: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.4: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.5: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.6: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.7: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.8: `libsndfile` — affected >=0 <1.0.28-r0
- Alpine:v3.9: `libsndfile` — affected >=0 <1.0.28-r0

## Details
In libsndfile before 1.0.28, an error in the "flac_buffer_copy()" function (flac.c) can be exploited to cause a stack-based buffer overflow via a specially crafted FLAC file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7585
