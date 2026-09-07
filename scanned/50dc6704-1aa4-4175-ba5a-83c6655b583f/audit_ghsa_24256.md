# [M] Zope Cross-site scripting (XSS) vulnerability in ZMI pages

## Summary
Severity: Medium
Advisory: GHSA-5r4x-qc7q-vj27
CVE: CVE-2009-5145
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-5r4x-qc7q-vj27
Type: github-advisory

## Affected
- PyPI: `Zope2` — affected >=0 <2.12.5

## Details
Cross-site scripting (XSS) vulnerability in ZMI pages that use the manage_tabs_message in Zope 2.11.4, 2.11.2, 2.10.9, 2.10.7, 2.10.6, 2.10.5, 2.10.4, 2.10.2, 2.10.1, 2.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-5145
- https://github.com/zopefoundation/Zope/commit/2abdf14620f146857dc8e3ffd2b6a754884c331d
- https://bugs.launchpad.net/zope2/+bug/490514
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2017-148.yaml
- https://github.com/zopefoundation/Zope
- https://security-tracker.debian.org/tracker/CVE-2009-5145
- http://cve.killedkenny.io/cve/CVE-2009-5145
- http://www.openwall.com/lists/oss-security/2015/03/02/7
