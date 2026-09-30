# [H] ALPINE-CVE-2020-6105

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-6105
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-6105
Type: osv

## Affected
- Alpine:v3.13: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.14: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.15: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.16: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.17: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.18: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.19: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.20: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.21: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.22: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.23: `f2fs-tools` — affected >=0 <1.14.0-r0
- Alpine:v3.24: `f2fs-tools` — affected >=0 <1.14.0-r0

## Details
An exploitable code execution vulnerability exists in the multiple devices functionality of F2fs-Tools F2fs.Fsck 1.13. A specially crafted f2fs filesystem can cause Information overwrite resulting in a code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-6105
