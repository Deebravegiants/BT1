# [C] CVE-2020-8086

## Summary
Severity: Critical
Advisory: CVE-2020-8086
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2020-8086
Type: osv

## Details
The mod_auth_ldap and mod_auth_ldap2 Community Modules through 2020-01-27 for Prosody incompletely verify the XMPP address passed to the is_admin() function. This grants remote entities admin-only functionality if their username matches the username of a local admin.

## References
- https://prosody.im/security/advisory_20200128/
- https://seclists.org/bugtraq/2020/Feb/5
- https://www.debian.org/security/2020/dsa-4612
- https://hg.prosody.im/prosody-modules/log/tip/mod_auth_ldap/mod_auth_ldap.lua
- https://hg.prosody.im/prosody-modules/log/tip/mod_auth_ldap2/mod_auth_ldap2.lua
