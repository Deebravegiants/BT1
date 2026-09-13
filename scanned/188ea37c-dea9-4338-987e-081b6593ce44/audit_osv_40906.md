# [M] dhcpcd Stack Out-of-Bounds Write in dhcp6_makemessage()

## Summary
Severity: Medium
Advisory: CVE-2026-56114
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56114
Type: osv

## Details
dhcpcd through 10.3.2, fixed in commit 2f00c7b, contains a one-byte stack out-of-bounds write vulnerability in dhcp6_makemessage() in src/dhcp6.c that allows unauthenticated same-link attackers to write beyond a fixed local buffer by serializing an oversized RFC6603 OPTION_PD_EXCLUDE option body. Attackers can send a crafted DHCPv6 ADVERTISE message containing an IA_PD IAPREFIX /0 with a valid OPTION_PD_EXCLUDE using an exclude prefix length of /121 through /128 to trigger the out-of-bounds write and potentially corrupt adjacent stack memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56114.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56114
- https://www.vulncheck.com/advisories/dhcpcd-stack-out-of-bounds-write-in-dhcp6-makemessage
- https://github.com/NetworkConfiguration/dhcpcd/commit/2f00c7bfc408b6582d331932dfa47829c4819029
- https://github.com/NetworkConfiguration/dhcpcd
