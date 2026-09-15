# [H] ALPINE-CVE-2019-6470

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6470
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6470
Type: osv

## Affected
- Alpine:v3.11: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.12: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.13: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.14: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.15: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.16: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.17: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.18: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.19: `dhcp` — affected >=0 <4.4.1-r0
- Alpine:v3.20: `dhcp` — affected >=0 <4.4.1-r0

## Details
There had existed in one of the ISC BIND libraries a bug in a function that was used by dhcpd when operating in DHCPv6 mode. There was also a bug in dhcpd relating to the use of this function per its documentation, but the bug in the library function prevented this from causing any harm. All releases of dhcpd from ISC contain copies of this, and other, BIND libraries in combinations that have been tested prior to release and are known to not present issues like this. Some third-party packagers of ISC software have modified the dhcpd source, BIND source, or version matchup in ways that create the crash potential. Based on reports available to ISC, the crash probability is large and no analysis has been done on how, or even if, the probability can be manipulated by an attacker. Affects: Builds of dhcpd versions prior to version 4.4.1 when using BIND versions 9.11.2 or later, or BIND versions with specific bug fixes backported to them. ISC does not have access to comprehensive version lists for all repackagings of dhcpd that are vulnerable. In particular, builds from other vendors may also be affected. Operators are advised to consult their vendor documentation.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6470
