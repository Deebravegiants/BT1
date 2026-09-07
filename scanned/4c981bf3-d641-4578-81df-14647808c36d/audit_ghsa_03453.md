# [C] Command injection in corenlp-js-prefab

## Summary
Severity: Critical
Advisory: GHSA-h73g-8g27-xxcx
CVE: CVE-2020-28439
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-h73g-8g27-xxcx
Type: github-advisory

## Affected
- npm: `corenlp-js-prefab` — affected >=0

## Details
This affects all versions of package corenlp-js-prefab. The injection point is located in line 10 in 'index.js.' It depends on a vulnerable package 'corenlp-js-interface.'

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28439
- https://snyk.io/vuln/SNYK-JS-CORENLPJSPREFAB-1050434
