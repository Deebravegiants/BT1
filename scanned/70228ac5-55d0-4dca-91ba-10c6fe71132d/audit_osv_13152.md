# [M] CVE-2018-18065

## Summary
Severity: Medium
Advisory: CVE-2018-18065
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/CVE-2018-18065
Type: osv

## Details
_set_key in agent/helpers/table_container.c in Net-SNMP before 5.8 has a NULL Pointer Exception bug that can be used by an authenticated attacker to remotely cause the instance to crash via a crafted UDP packet, resulting in Denial of Service.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-978220.pdf
- https://security.paloaltonetworks.com/CVE-2018-18065
- http://www.securityfocus.com/bid/106265
- https://security.netapp.com/advisory/ntap-20181107-0001/
- https://usn.ubuntu.com/3792-1/
- https://usn.ubuntu.com/3792-2/
- https://usn.ubuntu.com/3792-3/
- https://www.debian.org/security/2018/dsa-4314
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://dumpco.re/blog/net-snmp-5.7.3-remote-dos
- https://sourceforge.net/p/net-snmp/code/ci/7ffb8e25a0db851953155de91f0170e9bf8c457d/
- https://www.exploit-db.com/exploits/45547/
