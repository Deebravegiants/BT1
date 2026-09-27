# [M] ALPINE-CVE-2017-8363

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-8363
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8363
Type: osv

## Affected
- Alpine:v3.10: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.11: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.12: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.13: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.14: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.15: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.16: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.17: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.18: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.19: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.20: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.21: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.22: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.23: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.24: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.3: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.4: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.5: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.6: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.7: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.8: `libsndfile` — affected >=0 <1.0.28-r1
- Alpine:v3.9: `libsndfile` — affected >=0 <1.0.28-r1

## Details
The flac_buffer_copy function in flac.c in libsndfile 1.0.28 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8363
