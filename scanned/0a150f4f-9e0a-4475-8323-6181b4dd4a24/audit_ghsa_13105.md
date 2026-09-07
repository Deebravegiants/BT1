# [M] Apache Superset may expose internal traces on REST API endpoints

## Summary
Severity: Medium
Advisory: GHSA-cpvx-2365-466c
CVE: CVE-2023-39264
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-cpvx-2365-466c
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
By default, stack traces for errors were enabled, which resulted in the exposure of internal traces on REST API endpoints to users. This vulnerability exists in Apache Superset versions up to and including 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39264
- https://github.com/apache/superset
- https://lists.apache.org/thread/y65t1of7hb445n86o1vdzjct7rfwlx75
