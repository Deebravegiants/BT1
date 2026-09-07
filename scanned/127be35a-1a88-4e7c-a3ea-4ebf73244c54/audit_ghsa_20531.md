# [M] Cross-site Scripting in Ericsson CodeChecker

## Summary
Severity: Medium
Advisory: GHSA-fxmx-pfm2-85m2
CVE: CVE-2021-44217
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-fxmx-pfm2-85m2
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0 <6.18.2

## Details
In Ericsson CodeChecker prior to 6.18.2, a Stored Cross-site scripting (XSS) vulnerability in the comments component of the reports viewer allows remote attackers to inject arbitrary web script or HTML via the POST JSON data of the /CodeCheckerService API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44217
- https://github.com/Ericsson/codechecker/pull/3549
- https://github.com/Ericsson/codechecker/commit/72ee51158e6d81150320223b85410c179b9ee2b1
- https://codechecker-demo.eastus.cloudapp.azure.com
- https://github.com/Ericsson/codechecker
- https://github.com/Ericsson/codechecker/releases
- https://github.com/Ericsson/codechecker/releases/tag/v6.18.2
- https://github.com/Hyperkopite/CVE-2021-44217/blob/main/README.md
- https://github.com/pypa/advisory-database/tree/main/vulns/codechecker-api/PYSEC-2022-43181.yaml
- https://user-images.githubusercontent.com/9525971/142965091-e118b012-a7fc-4c2f-ad0c-80aeed6f7ec9.png
