# [H] Plone Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-pcwm-8jc3-qxvj
CVE: CVE-2011-4462
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-pcwm-8jc3-qxvj
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <4.1.4

## Details
Plone 4.1.3 and earlier computes hash values for form parameters without restricting the ability to trigger hash collisions predictably, which allows remote attackers to cause a denial of service (CPU consumption) by sending many crafted parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4462
- https://exchange.xforce.ibmcloud.com/vulnerabilities/72018
- https://github.com/advisories/GHSA-pcwm-8jc3-qxvj
- https://github.com/plone/plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2011-22.yaml
- http://archives.neohapsis.com/archives/bugtraq/2011-12/0181.html
- http://www.kb.cert.org/vuls/id/903934
- http://www.nruns.com/_downloads/advisory28122011.pdf
- http://www.ocert.org/advisories/ocert-2011-003.html
