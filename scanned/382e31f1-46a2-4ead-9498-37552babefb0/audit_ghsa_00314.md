# [M] Cross-site scripting in Products.CMFPlone and Products.PasswordResetTool

## Summary
Severity: Medium
Advisory: GHSA-p7h9-vf92-5fj5
CVE: CVE-2011-1948
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-p7h9-vf92-5fj5
Type: github-advisory

## Affected
- PyPI: `Products.PasswordResetTool` — affected >=0 <2.0.6
- PyPI: `Products.CMFPlone` — affected >=0 <4.0.7
- PyPI: `Products.CMFPlone` — affected >=4.1a1 <4.1rc3
- PyPI: `Plone` — affected >=0 <4.1.1

## Details
Cross-site scripting (XSS) vulnerability in Plone 4.1 and earlier allows remote attackers to inject arbitrary web script or HTML via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1948
- https://access.redhat.com/errata/RHSA-2012:0151
- https://access.redhat.com/security/cve/CVE-2011-1948
- https://bugzilla.redhat.com/show_bug.cgi?id=711494
- https://exchange.xforce.ibmcloud.com/vulnerabilities/67693
- https://github.com/advisories/GHSA-p7h9-vf92-5fj5
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2011-14.yaml
- http://plone.org/products/plone/security/advisories/CVE-2011-1948
