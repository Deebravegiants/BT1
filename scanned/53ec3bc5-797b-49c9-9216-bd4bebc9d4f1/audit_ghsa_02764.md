# [H] XML2Dict XML Entity Expansion Vulnerability

## Summary
Severity: High
Advisory: GHSA-gp6m-vqhm-5cm5
CVE: CVE-2021-25951
CWE: CWE-611, CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-gp6m-vqhm-5cm5
Type: github-advisory

## Affected
- PyPI: `XML2Dict` — affected >=0

## Details
XXE vulnerability in 'XML2Dict' version 0.2.2 allows an attacker to cause a denial of service. The parse function does not properly restrict recursive entity references.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25951
- https://github.com/mcspring/XML2Dict/tree/master
- https://github.com/mcspring/xml2dict
- https://github.com/pypa/advisory-database/tree/main/vulns/xml2dict/PYSEC-2021-349.yaml
- https://pypi.org/project/XML2Dict
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25951
