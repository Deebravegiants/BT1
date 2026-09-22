# [H] Regular Expression Denial of Service in Leo Editor

## Summary
Severity: High
Advisory: GHSA-x38q-xg2h-rxgx
CVE: CVE-2020-23478
CWE: CWE-1333, CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-x38q-xg2h-rxgx
Type: github-advisory

## Affected
- PyPI: `leo` — affected >=0 <6.3

## Details
Leo Editor v6.2.1 was discovered to contain a regular expression denial of service (ReDoS) vulnerability in the component plugins/importers/dart.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23478
- https://github.com/leo-editor/leo-editor/issues/1597
- https://github.com/leo-editor/leo-editor/commit/029833689060ee73f1bc1708cf4b182f0c66ec8e
- https://github.com/advisories/GHSA-x38q-xg2h-rxgx
- https://github.com/leo-editor/leo-editor
- https://github.com/pypa/advisory-database/tree/main/vulns/leo/PYSEC-2021-338.yaml
