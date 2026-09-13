# [H] HTTP header injection in Plone and Zope2

## Summary
Severity: High
Advisory: GHSA-77hv-8796-8ccp
CVE: CVE-2012-5486
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-77hv-8796-8ccp
Type: github-advisory

## Affected
- PyPI: `Zope2` — affected >=0 <2.13.19
- PyPI: `Plone` — affected >=3.3.2 <4.2.3
- PyPI: `Plone` — affected >=4.3a1 <4.3b1

## Details
ZPublisher.HTTPRequest._scrubHeader in Zope 2 before 2.13.19, as used in Plone before 4.3 beta 1, allows remote attackers to inject arbitrary HTTP headers via a linefeed (LF) character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5486
- https://access.redhat.com/errata/RHSA-2014:1194
- https://access.redhat.com/security/cve/CVE-2012-5486
- https://bugs.launchpad.net/zope2/+bug/930812
- https://bugzilla.redhat.com/show_bug.cgi?id=878939
- https://github.com/advisories/GHSA-77hv-8796-8ccp
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-28.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/zope2/PYSEC-2014-73.yaml
- https://plone.org/products/plone-hotfix/releases/20121106
- https://plone.org/products/plone/security/advisories/20121106/02
- http://rhn.redhat.com/errata/RHSA-2014-1194.html
- http://www.openwall.com/lists/oss-security/2012/11/10/1
