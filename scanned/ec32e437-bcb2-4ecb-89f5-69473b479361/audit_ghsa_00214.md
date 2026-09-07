# [M] Plone Sandbox Escape

## Summary
Severity: Medium
Advisory: GHSA-p5wr-vp8g-q5p4
CVE: CVE-2017-5524
CWE: CWE-134
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-p5wr-vp8g-q5p4
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=4.0 <4.3.12
- PyPI: `Plone` — affected >=5.1a1 <5.1b1
- PyPI: `Plone` — affected >=5.0rc1 <5.0.7

## Details
Plone 4.x through 4.3.11 and 5.x through 5.0.6 allow remote attackers to bypass a sandbox protection mechanism and obtain sensitive information by leveraging the Python string format method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5524
- https://github.com/plone/Products.CMFPlone/pull/1912
- https://github.com/plone/Products.CMFPlone/commit/a7d47692058e10ce89968e7ca4dacbdf44fcad4f
- https://github.com/advisories/GHSA-p5wr-vp8g-q5p4
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2017-81.yaml
- https://plone.org/security/hotfix/20170117/sandbox-escape
- http://www.openwall.com/lists/oss-security/2017/01/18/6
- http://www.securityfocus.com/bid/95679
