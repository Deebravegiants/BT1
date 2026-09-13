# [H] ALPINE-CVE-2026-11771

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11771
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11771
Type: osv

## Affected
- Alpine:v3.24: `openvpn` — affected >=2.1.0 <2.7.5-r0

## Details
OpenVPN version 2.1.0 through 2.6.20 and 2.7_alpha1 through 2.7.4 allows attackers via an off-by-one buffer write in the NTLM proxy authentication to potentially cause a crash via a crafted NTLM response from a malicious proxy server

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11771
