# [C] ALPINE-CVE-2026-27784

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-27784
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27784
Type: osv

## Affected
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.24: `nginx` — affected >=0 <1.28.3-r0

## Details
The 32-bit implementation of NGINX Open Source has a vulnerability in the ngx_http_mp4_module module, which might allow an attacker to over-read or over-write NGINX worker memory resulting in its termination, using a specially crafted MP4 file. The issue only affects 32-bit NGINX Open Source if it is built with the ngx_http_mp4_module module and the mp4 directive is used in the configuration file. Additionally, the attack is possible only if an attacker can trigger the processing of a specially crafted MP4 file with the ngx_http_mp4_module module. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27784
