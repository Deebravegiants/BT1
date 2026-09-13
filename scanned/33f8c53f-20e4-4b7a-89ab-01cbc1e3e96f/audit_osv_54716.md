# [M] CVE-2024-28820

## Summary
Severity: Medium
Advisory: CVE-2024-28820
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-28820
Type: osv

## Details
Buffer overflow in the extract_openvpn_cr function in openvpn-cr.c in openvpn-auth-ldap (aka the Three Rings Auth-LDAP plugin for OpenVPN) 2.0.4 allows attackers with a valid LDAP username and who can control the challenge/response password field to pass a string with more than 14 colons into this field and cause a buffer overflow.

## References
- https://github.com/threerings/openvpn-auth-ldap/tags
- https://github.com/threerings/openvpn-auth-ldap/pull/92
