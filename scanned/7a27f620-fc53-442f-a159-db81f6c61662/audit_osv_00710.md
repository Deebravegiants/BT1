# [M] ALPINE-CVE-2017-6508

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-6508
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6508
Type: osv

## Affected
- Alpine:v3.10: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.11: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.12: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.13: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.14: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.15: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.16: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.17: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.18: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.19: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.2: `wget` — affected >=0 <1.18-r1
- Alpine:v3.20: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.21: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.22: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.23: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.24: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.3: `wget` — affected >=0 <1.17.1-r2
- Alpine:v3.4: `wget` — affected >=0 <1.18-r1
- Alpine:v3.6: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.7: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.8: `wget` — affected >=0 <1.19.1-r1
- Alpine:v3.9: `wget` — affected >=0 <1.19.1-r1

## Details
CRLF injection vulnerability in the url_parse function in url.c in Wget through 1.19.1 allows remote attackers to inject arbitrary HTTP headers via CRLF sequences in the host subcomponent of a URL.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6508
