# [C] CVE-2016-6254

## Summary
Severity: Critical
Advisory: CVE-2016-6254
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/CVE-2016-6254
Type: osv

## Details
Heap-based buffer overflow in the parse_packet function in network.c in collectd before 5.4.3 and 5.x before 5.5.2 allows remote attackers to cause a denial of service (daemon crash) or possibly execute arbitrary code via a crafted network packet.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CM4W5SJ4OTBGINGIN4NJLXCUZAZANO6J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UIZ5UXDOB7BA5NGE2F2I2BL4K6763DHW/
- http://collectd.org/news.shtml
- http://www.debian.org/security/2016/dsa-3636
- https://github.com/collectd/collectd/commit/b589096f907052b3a4da2b9ccc9b0e2e888dfc18
