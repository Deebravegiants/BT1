# [C] ALPINE-CVE-2018-14767

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-14767
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14767
Type: osv

## Affected
- Alpine:v3.10: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.11: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.12: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.13: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.14: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.15: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.16: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.17: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.18: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.19: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.20: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.21: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.22: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.23: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.24: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.6: `kamailio` — affected >=5.1.0 <5.0.2-r4
- Alpine:v3.7: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.8: `kamailio` — affected >=5.1.0 <5.1.4-r0
- Alpine:v3.9: `kamailio` — affected >=5.1.0 <5.1.4-r0

## Details
In Kamailio before 5.0.7 and 5.1.x before 5.1.4, a crafted SIP message with a double "To" header and an empty "To" tag causes a segmentation fault and crash. The reason is missing input validation in the "build_res_buf_from_sip_req" core function. This could result in denial of service and potentially the execution of arbitrary code.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14767
