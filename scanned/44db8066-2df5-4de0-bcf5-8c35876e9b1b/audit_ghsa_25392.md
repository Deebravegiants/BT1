# [H] mod_cluster Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-68qq-3phh-53j7
CVE: CVE-2016-3110
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-68qq-3phh-53j7
Type: github-advisory

## Affected
- Maven: `org.jboss.mod_cluster:mod_cluster-parent` — affected >=0 <1.3.3.Final

## Details
mod_cluster, as used in Red Hat JBoss Web Server 2.1, allows remote attackers to cause a denial of service (Apache http server crash) via an MCMP message containing a series of = (equals) characters after a legitimate element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3110
- https://bugzilla.redhat.com/show_bug.cgi?id=1326320
- https://github.com/modcluster/mod_cluster
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6JMA2YLPK6SEUVF5Q3QEANHYEPRZA2RI
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CX5QNNIVAUB2VVDV6TR3YMFTL6VRKOBO
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HE5YZTBZRXCMQFT5LDLZG2HAYBKMYQLL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6JMA2YLPK6SEUVF5Q3QEANHYEPRZA2RI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CX5QNNIVAUB2VVDV6TR3YMFTL6VRKOBO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HE5YZTBZRXCMQFT5LDLZG2HAYBKMYQLL
- https://web.archive.org/web/20200227231527/http://www.securityfocus.com/bid/92584
- http://rhn.redhat.com/errata/RHSA-2016-1648.html
- http://rhn.redhat.com/errata/RHSA-2016-1649.html
- http://rhn.redhat.com/errata/RHSA-2016-1650.html
- http://rhn.redhat.com/errata/RHSA-2016-2054.html
- http://rhn.redhat.com/errata/RHSA-2016-2055.html
- http://rhn.redhat.com/errata/RHSA-2016-2056.html
