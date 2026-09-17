# [C] Code injection in ymlref

## Summary
Severity: Critical
Advisory: GHSA-8r8j-xvfj-36f9
CVE: CVE-2018-20133
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-19
Source: https://github.com/advisories/GHSA-8r8j-xvfj-36f9
Type: github-advisory

## Affected
- PyPI: `ymlref` — affected >=0

## Details
ymlref is a library that allows to load Yaml documents and resolve JSON-pointer references inside them. ymlref versions up to 0.1.1 allow code injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20133
- https://github.com/dexter2206/ymlref/issues/2
- https://github.com/dexter2206/ymlref
- https://github.com/pypa/advisory-database/tree/main/vulns/ymlref/PYSEC-2018-103.yaml
