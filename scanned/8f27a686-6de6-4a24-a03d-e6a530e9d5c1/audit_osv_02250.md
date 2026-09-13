# [H] ALPINE-CVE-2021-35940

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-35940
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-35940
Type: osv

## Affected
- Alpine:v3.14: `apr` — affected >=0 <1.7.0-r1
- Alpine:v3.15: `apr` — affected >=0 <1.7.0-r1
- Alpine:v3.16: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.17: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.18: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.19: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.20: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.21: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.22: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.23: `apr` — affected >=0 <1.7.0-r2
- Alpine:v3.24: `apr` — affected >=0 <1.7.0-r2

## Details
An out-of-bounds array read in the apr_time_exp*() functions was fixed in the Apache Portable Runtime 1.6.3 release (CVE-2017-12613). The fix for this issue was not carried forward to the APR 1.7.x branch, and hence version 1.7.0 regressed compared to 1.6.3 and is vulnerable to the same issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-35940
