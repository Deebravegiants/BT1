# [M] ALPINE-CVE-2026-3012

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-3012
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3012
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=4.16.0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=4.16.0 <4.23.8-r0

## Details
A flaw was found in Samba’s certificate auto-enrollment Group Policy handling. When certificate auto-enrollment is enabled, Samba may retrieve a CA certificate over an unencrypted HTTP connection and install it into the local trust store without proper verification. An attacker with the ability to intercept or redirect network traffic could exploit this behavior to supply a malicious certificate authority certificate, potentially allowing interception or spoofing of trusted communications.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3012
