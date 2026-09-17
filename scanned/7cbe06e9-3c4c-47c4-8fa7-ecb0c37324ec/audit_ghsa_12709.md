# [H] requests-xml XML External Entity Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-ccrc-9x59-3vc4
CVE: CVE-2020-26708
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-29
Source: https://github.com/advisories/GHSA-ccrc-9x59-3vc4
Type: github-advisory

## Affected
- PyPI: `requests-xml` — affected >=0

## Details
requests-xml v0.2.3 was discovered to contain an XML External Entity Injection (XXE) vulnerability which allows attackers to execute arbitrary code via a crafted XML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26708
- https://github.com/erinxocon/requests-xml/issues/7
- https://github.com/erinxocon/requests-xml
- https://github.com/pypa/advisory-database/tree/main/vulns/requests-xml/PYSEC-2023-96.yaml
- https://security.netapp.com/advisory/ntap-20230908-0003
