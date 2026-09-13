# [M] ALPINE-CVE-2019-20633

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20633
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20633
Type: osv

## Affected
- Alpine:v3.11: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.12: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.13: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.14: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.15: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.16: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.17: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.18: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.19: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.20: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.21: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.22: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.23: `patch` — affected >=0 <2.7.6-r7
- Alpine:v3.24: `patch` — affected >=0 <2.7.6-r7

## Details
GNU patch through 2.7.6 contains a free(p_line[p_end]) Double Free vulnerability in the function another_hunk in pch.c that can cause a denial of service via a crafted patch file. NOTE: this issue exists because of an incomplete fix for CVE-2018-6952.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20633
