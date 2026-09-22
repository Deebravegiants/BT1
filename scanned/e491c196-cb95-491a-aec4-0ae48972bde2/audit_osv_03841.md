# [M] ALPINE-CVE-2026-56114

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56114
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56114
Type: osv

## Affected
- Alpine:v3.23: `dhcpcd` — affected >=0 <10.5.2-r0
- Alpine:v3.24: `dhcpcd` — affected >=0 <10.5.2-r0

## Details
dhcpcd through 10.3.2, fixed in commit 2f00c7b, contains a one-byte stack out-of-bounds write vulnerability in dhcp6_makemessage() in src/dhcp6.c that allows unauthenticated same-link attackers to write beyond a fixed local buffer by serializing an oversized RFC6603 OPTION_PD_EXCLUDE option body. Attackers can send a crafted DHCPv6 ADVERTISE message containing an IA_PD IAPREFIX /0 with a valid OPTION_PD_EXCLUDE using an exclude prefix length of /121 through /128 to trigger the out-of-bounds write and potentially corrupt adjacent stack memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56114
