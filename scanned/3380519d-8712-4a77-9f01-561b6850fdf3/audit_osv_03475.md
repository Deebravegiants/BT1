# [M] ALPINE-CVE-2026-1642

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-1642
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1642
Type: osv

## Affected
- Alpine:v3.22: `nginx` — affected >=0 <1.28.2-r0
- Alpine:v3.23: `nginx` — affected >=0 <1.28.2-r0
- Alpine:v3.24: `nginx` — affected >=0 <1.28.2-r0

## Details
A vulnerability exists in NGINX OSS and NGINX Plus when configured to proxy to upstream Transport Layer Security (TLS) servers. An attacker with a man-in-the-middle (MITM) position on the upstream server side—along with conditions beyond the attacker's control—may be able to inject plain text data into the response from an upstream proxied server.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1642
