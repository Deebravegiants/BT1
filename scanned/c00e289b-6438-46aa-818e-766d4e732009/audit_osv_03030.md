# [M] ALPINE-CVE-2024-28820

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-28820
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28820
Type: osv

## Affected
- Alpine:v3.21: `openvpn-auth-ldap` — affected >=0 <2.0.4-r7
- Alpine:v3.22: `openvpn-auth-ldap` — affected >=0 <2.0.4-r7
- Alpine:v3.23: `openvpn-auth-ldap` — affected >=0 <2.0.4-r7
- Alpine:v3.24: `openvpn-auth-ldap` — affected >=0 <2.0.4-r7

## Details
Buffer overflow in the extract_openvpn_cr function in openvpn-cr.c in openvpn-auth-ldap (aka the Three Rings Auth-LDAP plugin for OpenVPN) 2.0.4 allows attackers with a valid LDAP username and who can control the challenge/response password field to pass a string with more than 14 colons into this field and cause a buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28820
