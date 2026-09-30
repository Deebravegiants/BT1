# [M] ALPINE-CVE-2026-27651

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27651
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27651
Type: osv

## Affected
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.24: `nginx` — affected >=0 <1.28.3-r0

## Details
When the ngx_mail_auth_http_module module is enabled on NGINX Plus or NGINX Open Source, undisclosed requests can cause worker processes to terminate. This issue may occur when (1) CRAM-MD5 or APOP authentication is enabled, and (2) the authentication server permits retry by returning the Auth-Wait response header. Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27651
