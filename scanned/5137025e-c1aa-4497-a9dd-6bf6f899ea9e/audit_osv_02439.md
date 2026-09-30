# [M] ALPINE-CVE-2022-23960

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-23960
Ecosystem: Alpine:v3.12
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-03-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23960
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=0 <4.13.4-r3

## Details
Certain Arm Cortex and Neoverse processors through 2022-03-08 do not properly restrict cache speculation, aka Spectre-BHB. An attacker can leverage the shared branch history in the Branch History Buffer (BHB) to influence mispredicted branches. Then, cache allocation can allow the attacker to obtain sensitive information.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23960
