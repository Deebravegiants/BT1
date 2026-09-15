# [M] ALPINE-CVE-2023-49100

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-49100
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49100
Type: osv

## Affected
- Alpine:v3.18: `arm-trusted-firmware` — affected >=0 <2.8.14-r0
- Alpine:v3.19: `arm-trusted-firmware` — affected >=0 <2.8.14-r0
- Alpine:v3.20: `arm-trusted-firmware` — affected >=0 <2.8.14-r0

## Details
Trusted Firmware-A (TF-A) before 2.10 has a potential read out-of-bounds in the SDEI service. The input parameter passed in register x1 is not validated well enough in the function sdei_interrupt_bind. The parameter is passed to a call to plat_ic_get_interrupt_type. It can be any arbitrary value passing checks in the function plat_ic_is_sgi. A compromised Normal World (Linux kernel) can enable a root-privileged attacker to issue arbitrary SMC calls. Using this primitive, he can control the content of registers x0 through x6, which are used to send parameters to TF-A. Out-of-bounds addresses can be read in the context of TF-A (EL3). Because the read value is never returned to non-secure memory or in registers, no leak is possible. An attacker can still crash TF-A, however.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49100
