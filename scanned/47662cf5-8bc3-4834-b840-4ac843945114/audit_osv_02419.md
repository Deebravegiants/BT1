# [M] ALPINE-CVE-2022-22707

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-22707
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-22707
Type: osv

## Affected
- Alpine:v3.13: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.14: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.15: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.16: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.17: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.18: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.19: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.20: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.21: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.22: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.23: `lighttpd` — affected >=1.4.46 <1.4.64-r0
- Alpine:v3.24: `lighttpd` — affected >=1.4.46 <1.4.64-r0

## Details
In lighttpd 1.4.46 through 1.4.63, the mod_extforward_Forwarded function of the mod_extforward plugin has a stack-based buffer overflow (4 bytes representing -1), as demonstrated by remote denial of service (daemon crash) in a non-default configuration. The non-default configuration requires handling of the Forwarded header in a somewhat unusual manner. Also, a 32-bit system is much more likely to be affected than a 64-bit system.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-22707
