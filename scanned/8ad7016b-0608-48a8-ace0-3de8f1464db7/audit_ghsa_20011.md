# [M] liquidjs may leak properties of a prototype

## Summary
Severity: Medium
Advisory: GHSA-45rm-2893-5f49
CVE: CVE-2022-25948
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-45rm-2893-5f49
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.0.0

## Details
The package liquidjs before 10.0.0 is vulnerable to Information Exposure when `ownPropertyOnly` parameter is set to `False`, which results in leaking properties of a prototype. Workaround For versions 9.34.0 and higher, an option to disable this functionality is provided.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25948
- https://github.com/harttle/liquidjs/issues/454
- https://github.com/harttle/liquidjs/commit/7e99efc5131e20cf3f59e1fc2c371a15aa4109db
- https://github.com/harttle/liquidjs/commit/7eb621601c2b05d6e379e5ce42219f2b1f556208
- https://github.com/harttle/liquidjs
- https://groups.google.com/u/0/a/snyk.io/g/report/c/9ipXecWRtTM/m/IgLadevtCQAJ
- https://security.snyk.io/vuln/SNYK-JS-LIQUIDJS-2952868
