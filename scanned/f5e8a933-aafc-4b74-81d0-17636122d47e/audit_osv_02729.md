# [M] ALPINE-CVE-2022-4603

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-4603
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4603
Type: osv

## Affected
- Alpine:v3.14: `ppp` — affected >=0 <2.4.9-r1
- Alpine:v3.15: `ppp` — affected >=0 <2.4.9-r3
- Alpine:v3.16: `ppp` — affected >=0 <2.4.9-r4
- Alpine:v3.17: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.18: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.19: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.20: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.21: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.22: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.23: `ppp` — affected >=0 <2.4.9-r6
- Alpine:v3.24: `ppp` — affected >=0 <2.4.9-r6

## Details
A vulnerability classified as problematic has been found in ppp. Affected is the function dumpppp of the file pppdump/pppdump.c of the component pppdump. The manipulation of the argument spkt.buf/rpkt.buf leads to improper validation of array index. The real existence of this vulnerability is still doubted at the moment. The name of the patch is a75fb7b198eed50d769c80c36629f38346882cbf. It is recommended to apply a patch to fix this issue. VDB-216198 is the identifier assigned to this vulnerability. NOTE: pppdump is not used in normal process of setting up a PPP connection, is not installed setuid-root, and is not invoked automatically in any scenario.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4603
