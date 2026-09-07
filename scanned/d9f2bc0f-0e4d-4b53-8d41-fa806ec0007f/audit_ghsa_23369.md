# [H] Loop with Unreachable Exit Condition in Netty

## Summary
Severity: High
Advisory: GHSA-rv63-gqm8-9w8q
CVE: CVE-2016-4970
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rv63-gqm8-9w8q
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.0.0.Alpha1 <4.0.37.Final
- Maven: `io.netty:netty-handler` — affected >=4.1.0.Beta1 <4.1.1.Final

## Details
handler/ssl/OpenSslEngine.java in Netty 4.0.x before 4.0.37.Final and 4.1.x before 4.1.1.Final allows remote attackers to cause a denial of service (infinite loop).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4970
- https://github.com/netty/netty/pull/5364
- https://bugzilla.redhat.com/show_bug.cgi?id=1343616
- https://github.com/netty/netty
- https://lists.apache.org/thread.html/afaa5860e3a6d327eb96c3d82cbd2f5996de815a16854ed1ad310144@%3Ccommits.cassandra.apache.org%3E
- https://wiki.opendaylight.org/view/Security_Advisories
- http://netty.io/news/2016/06/07/4-0-37-Final.html
- http://netty.io/news/2016/06/07/4-1-1-Final.html
- http://rhn.redhat.com/errata/RHSA-2017-0179.html
- http://rhn.redhat.com/errata/RHSA-2017-1097.html
