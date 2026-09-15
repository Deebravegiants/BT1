# [M] CVE-2022-37704

## Summary
Severity: Medium
Advisory: CVE-2022-37704
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2022-37704
Type: osv

## Details
Amanda 3.5.1 allows privilege escalation from the regular user backup to root. The SUID binary located at /lib/amanda/rundump will execute /usr/sbin/dump as root with controlled arguments from the attacker which may lead to escalation of privileges, denial of service, and information disclosure.

## References
- http://www.amanda.org/
- https://github.com/zmanda/amanda/releases/tag/tag-community-3.5.3
- https://lists.debian.org/debian-lts-announce/2024/09/msg00023.html
- https://marc.info/?l=amanda-hackers
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37704.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5DCLSX5YYTWMKSMDL67M5STZ5ZDSOXK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ATMGMVS3QDN6OMKMHGUTUTU7NS7HR3BZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYREA6LFXF5M7K4WLNJV5VNQPS4MTBW2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-37704
- https://github.com/zmanda/amanda/issues/192
- https://github.com/zmanda/amanda/pull/197
- https://github.com/zmanda/amanda/pull/205
- https://github.com/MaherAzzouzi/CVE-2022-37704
- https://lists.debian.org/debian-lts-announce/2023/02/msg00025.html
