# [M] CVE-2022-44793

## Summary
Severity: Medium
Advisory: CVE-2022-44793
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-07
Source: https://osv.dev/vulnerability/CVE-2022-44793
Type: osv

## Details
handle_ipv6IpForwarding in agent/mibgroup/ip-mib/ip_scalars.c in Net-SNMP 5.4.3 through 5.9.3 has a NULL Pointer Exception bug that can be used by a remote attacker to cause the instance to crash via a crafted UDP packet, resulting in Denial of Service.

## References
- https://gist.github.com/menglong2234/d07a65b5028145c9f4e1d1db8c4c202f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44793.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44793
- https://security.netapp.com/advisory/ntap-20230223-0011/
- https://github.com/net-snmp/net-snmp/issues/475
- https://lists.debian.org/debian-lts-announce/2023/01/msg00010.html
