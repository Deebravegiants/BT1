# [M] OpenStack Swift Cross-site Scriping vulnerability

## Summary
Severity: Medium
Advisory: GHSA-66vj-393f-hxfv
CVE: CVE-2014-3497
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-66vj-393f-hxfv
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=1.11.0 <2.0.0

## Details
Cross-site scripting (XSS) vulnerability in OpenStack Swift 1.11.0 through 1.13.1 allows remote attackers to inject arbitrary web script or HTML via the WWW-Authenticate header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3497
- https://access.redhat.com/errata/RHSA-2014:0941
- https://access.redhat.com/security/cve/CVE-2014-3497
- https://bugzilla.redhat.com/show_bug.cgi?id=1110809
- https://opendev.org/openstack/swift
- https://review.openstack.org/#/c/101031
- https://review.openstack.org/#/c/101032
- https://web.archive.org/web/20200229060002/http://www.securityfocus.com/bid/68116
- http://lists.openstack.org/pipermail/openstack-announce/2014-June/000243.html
- http://www.openwall.com/lists/oss-security/2014/06/19/10
- http://www.ubuntu.com/usn/USN-2256-1
