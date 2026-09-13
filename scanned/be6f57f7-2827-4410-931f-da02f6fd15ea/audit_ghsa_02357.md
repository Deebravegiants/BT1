# [M] XML External Entity Reference in Glances

## Summary
Severity: Medium
Advisory: GHSA-r2mj-8wgq-73m6
CVE: CVE-2021-23418
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-r2mj-8wgq-73m6
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <3.2.1

## Details
The package glances before 3.2.1 are vulnerable to XML External Entity (XXE) Injection via the use of Fault to parse untrusted XML data, which is known to be vulnerable to XML attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23418
- https://github.com/nicolargo/glances/issues/1025
- https://github.com/nicolargo/glances/commit/4b87e979afdc06d98ed1b48da31e69eaa3a9fb94
- https://github.com/nicolargo/glances/commit/85d5a6b4af31fcf785d5a61086cbbd166b40b07a
- https://github.com/nicolargo/glances/commit/9d6051be4a42f692392049fdbfc85d5dfa458b32
- https://github.com/advisories/GHSA-r2mj-8wgq-73m6
- https://github.com/nicolargo/glances
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2021-115.yaml
- https://snyk.io/vuln/SNYK-PYTHON-GLANCES-1311807
