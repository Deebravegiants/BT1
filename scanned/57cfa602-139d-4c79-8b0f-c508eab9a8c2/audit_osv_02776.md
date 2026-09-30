# [C] ALPINE-CVE-2023-23914

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-23914
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23914
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=7.77.0 <7.79.1-r5
- Alpine:v3.15: `curl` — affected >=7.77.0 <7.80.0-r6
- Alpine:v3.16: `curl` — affected >=7.77.0 <7.83.1-r6
- Alpine:v3.17: `curl` — affected >=7.77.0 <7.87.0-r2
- Alpine:v3.18: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.19: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.20: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.21: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.22: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.23: `curl` — affected >=7.77.0 <7.88.0-r0
- Alpine:v3.24: `curl` — affected >=7.77.0 <7.88.0-r0

## Details
A cleartext transmission of sensitive information vulnerability exists in curl <v7.88.0 that could cause HSTS functionality fail when multiple URLs are requested serially. Using its HSTS support, curl can be instructed to use HTTPS instead of usingan insecure clear-text HTTP step even when HTTP is provided in the URL. ThisHSTS mechanism would however surprisingly be ignored by subsequent transferswhen done on the same command line because the state would not be properlycarried on.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23914
