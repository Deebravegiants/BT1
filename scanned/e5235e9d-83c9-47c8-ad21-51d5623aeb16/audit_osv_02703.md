# [M] ALPINE-CVE-2022-43241

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-43241
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43241
Type: osv

## Affected
- Alpine:v3.14: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.15: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.16: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.17: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.18: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.19: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.20: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.21: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.22: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.23: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.24: `libde265` — affected >=0 <1.0.11-r0

## Details
Libde265 v1.0.8 was discovered to contain an unknown crash via ff_hevc_put_hevc_qpel_v_3_8_sse in sse-motion.cc. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted video file.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43241
