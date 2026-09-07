# [H] XML External Entity vulnerability in Easy-XML

## Summary
Severity: High
Advisory: GHSA-v899-28g4-qmh8
CVE: CVE-2020-26705
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-01
Source: https://github.com/advisories/GHSA-v899-28g4-qmh8
Type: github-advisory

## Affected
- PyPI: `easy-xml` — affected >=0

## Details
The parseXML function in Easy-XML 0.5.0 was discovered to have a XML External Entity (XXE) vulnerability which allows for an attacker to expose sensitive data or perform a denial of service (DOS) via a crafted external entity entered into the XML content as input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26705
- https://github.com/darkfoxprime/python-easy_xml/issues/1
- https://github.com/advisories/GHSA-v899-28g4-qmh8
- https://github.com/darkfoxprime/python-easy_xml
- https://github.com/pypa/advisory-database/tree/main/vulns/easy-xml/PYSEC-2021-388.yaml
