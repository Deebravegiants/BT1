# [M] CVE-2019-16168

## Summary
Severity: Medium
Advisory: CVE-2019-16168
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16168
Type: osv

## Details
In SQLite through 3.29.0, whereLoopAddBtreeIndex in sqlite3.c can crash a browser or other application because of missing validation of a sqlite_stat1 sz field, aka a "severe division by zero in the query planner."

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XZARJHJJDBHI7CE5PZEBXS5HKK6HXKW2/
- https://www.mail-archive.com/sqlite-users%40mailinglists.sqlite.org/msg116312.html
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://security.gentoo.org/glsa/202003-16
- https://security.netapp.com/advisory/ntap-20190926-0003/
- https://security.netapp.com/advisory/ntap-20200122-0003/
- https://usn.ubuntu.com/4205-1/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.sqlite.org/src/info/e4598ecbdd18bd82945f6029013296690e719a62
- https://www.tenable.com/security/tns-2021-08
- https://www.tenable.com/security/tns-2021-11
- https://www.tenable.com/security/tns-2021-14
- https://www.sqlite.org/src/timeline?c=98357d8c1263920b
