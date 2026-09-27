# [M] net-snmp vulnerable to Improper Input Validation when SETing malformed OIDs in master agent and subagent simultaneously

## Summary
Severity: Medium
Advisory: CVE-2022-24806
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2022-24806
Type: osv

## Details
net-snmp provides various tools relating to the Simple Network Management Protocol. Prior to version 5.9.2, a user with read-write credentials can exploit an Improper Input Validation vulnerability when SETing malformed OIDs in master agent and subagent simultaneously. Version 5.9.2 contains a patch. Users should use strong SNMPv3 credentials and avoid sharing the credentials. Those who must use SNMPv1 or SNMPv2c should use a complex community string and enhance the protection by restricting access to a given IP address range.

## References
- https://lists.debian.org/debian-lts-announce/2022/08/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FX75KKGMO5XMV6JMQZF6KOG3JPFNQBY7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24806.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24806
- https://security.gentoo.org/glsa/202210-29
- https://www.debian.org/security/2022/dsa-5209
- https://bugzilla.redhat.com/show_bug.cgi?id=2103225
- https://github.com/net-snmp/net-snmp/commit/ce66eb97c17aa9a48bc079be7b65895266fa6775
- https://github.com/net-snmp/net-snmp
