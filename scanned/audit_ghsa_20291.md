# [C] Code Injection in metacalc

## Summary
Severity: Critical
Advisory: GHSA-5gc4-cx9x-9c43
CVE: CVE-2022-21122
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-5gc4-cx9x-9c43
Type: github-advisory

## Affected
- npm: `metacalc` — affected >=0 <0.0.2

## Details
The package metacalc before 0.0.2 is vulnerable to Arbitrary Code Execution when it exposes JavaScript's Math class to the v8 context. As the Math class is exposed to user-land, it can be used to get access to JavaScript's Function constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21122
- https://github.com/metarhia/metacalc/pull/16
- https://github.com/metarhia/metacalc/commit/625c23d63eabfa16fc815f5832b147b08d2144bd
- https://github.com/metarhia/metacalc
- https://snyk.io/vuln/SNYK-JS-METACALC-2826197
