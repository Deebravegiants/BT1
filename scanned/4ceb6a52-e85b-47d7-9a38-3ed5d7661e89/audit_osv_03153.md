# [C] ALPINE-CVE-2024-5660

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-5660
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-5660
Type: osv

## Affected
- Alpine:v3.18: `arm-trusted-firmware` — affected >=0 <2.8.32-r0
- Alpine:v3.19: `arm-trusted-firmware` — affected >=0 <2.8.32-r0
- Alpine:v3.20: `arm-trusted-firmware` — affected >=0 <2.8.32-r0
- Alpine:v3.21: `arm-trusted-firmware` — affected >=0 <2.8.32-r0

## Details
Use of Hardware Page Aggregation (HPA) and Stage-1 and/or Stage-2 translation on Cortex-A77, Cortex-A78, Cortex-A78C, Cortex-A78AE, Cortex-A710, Cortex-X1, Cortex-X1C, Cortex-X2, Cortex-X3, Cortex-X4, Cortex-X925, Neoverse V1, Neoverse V2, Neoverse V3, Neoverse V3AE, Neoverse N2 may permit bypass of Stage-2 translation and/or GPT protection.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-5660
