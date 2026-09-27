# [M] CVE-2019-20892

## Summary
Severity: Medium
Advisory: CVE-2019-20892
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-25
Source: https://osv.dev/vulnerability/CVE-2019-20892
Type: osv

## Details
net-snmp before 5.8.1.pre1 has a double free in usm_free_usmStateReference in snmplib/snmpusm.c via an SNMPv3 GetBulk request. NOTE: this affects net-snmp packages shipped to end users by multiple Linux distributions, but might not affect an upstream release.

## References
- https://security.gentoo.org/glsa/202008-12
- https://usn.ubuntu.com/4410-1/
- https://bugs.launchpad.net/ubuntu/+source/net-snmp/+bug/1877027
- https://bugzilla.redhat.com/show_bug.cgi?id=1663027
- https://github.com/net-snmp/net-snmp/commit/5f881d3bf24599b90d67a45cae7a3eb099cd71c9
- https://www.oracle.com/security-alerts/cpujan2021.html
- http://www.openwall.com/lists/oss-security/2020/06/25/4
- https://sourceforge.net/p/net-snmp/bugs/2923/
