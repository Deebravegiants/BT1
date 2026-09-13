# [M] XML Entity Expansion (XEE) in Django

## Summary
Severity: Medium
Advisory: GHSA-qrh7-x6fp-c2mp
CVE: CVE-2013-1664
CWE: CWE-611
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qrh7-x6fp-c2mp
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.3.0 <1.3.6
- PyPI: `Django` — affected >=1.4.0 <1.4.4

## Details
The XML libraries for Python, as used in OpenStack Keystone Essex, Folsom, and Grizzly; Compute (Nova) Essex and Folsom; Cinder Folsom; Django; and possibly other products allow remote attackers to cause a denial of service (resource consumption and crash) via an XML Entity Expansion (XEE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1664
- https://github.com/django/django/commit/1c60d07ba23e0350351c278ad28d0bd5aa410b40
- https://github.com/django/django/commit/d19a27066b2247102e65412aa66917aff0091112
- https://bugs.launchpad.net/nova/+bug/1100282
- https://github.com/django/django
- http://blog.python.org/2013/02/announcing-defusedxml-fixes-for-xml.html
- http://bugs.python.org/issue17239
- http://lists.openstack.org/pipermail/openstack-announce/2013-February/000078.html
- http://rhn.redhat.com/errata/RHSA-2013-0657.html
- http://rhn.redhat.com/errata/RHSA-2013-0658.html
- http://rhn.redhat.com/errata/RHSA-2013-0670.html
- http://ubuntu.com/usn/usn-1757-1
- http://www.openwall.com/lists/oss-security/2013/02/19/2
- http://www.openwall.com/lists/oss-security/2013/02/19/4
