# [H] py-xml XML External Entity Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-j6v2-mwxm-f952
CVE: CVE-2020-26709
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-29
Source: https://github.com/advisories/GHSA-j6v2-mwxm-f952
Type: github-advisory

## Affected
- PyPI: `py-xml` — affected >=0

## Details
py-xml v1.0 was discovered to contain an XML External Entity Injection (XXE) vulnerability which allows attackers to execute arbitrary code via a crafted XML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26709
- https://github.com/PinaeOS/py-xml/issues/2
- https://github.com/PinaeOS/py-xml
- https://github.com/pypa/advisory-database/tree/main/vulns/py-xml/PYSEC-2023-95.yaml
