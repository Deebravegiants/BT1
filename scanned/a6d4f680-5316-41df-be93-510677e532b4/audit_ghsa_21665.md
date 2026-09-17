# [H] Prototype Pollution in object-path-set

## Summary
Severity: High
Advisory: GHSA-h6pr-c536-6rjg
CVE: CVE-2021-23507
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-05
Source: https://github.com/advisories/GHSA-h6pr-c536-6rjg
Type: github-advisory

## Affected
- npm: `object-path-set` — affected >=0 <1.0.2

## Details
The package object-path-set before 1.0.2 are vulnerable to Prototype Pollution via the setPath method, as it allows an attacker to merge object prototypes into it. *Note:* This vulnerability derives from an incomplete fix in https://security.snyk.io/vuln/SNYK-JS-OBJECTPATHSET-607908

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23507
- https://github.com/skratchdot/object-path-set/commit/2d67a714159c4099589b6661fa84e6d2adc31761
- https://github.com/skratchdot/object-path-set
- https://github.com/skratchdot/object-path-set/blob/577f5299fed15bb9edd11c940ff3cf0b9f4748d5/index.js%23L8
- https://snyk.io/blog/remediate-javascript-type-confusion-bypassed-input-validation
- https://snyk.io/vuln/SNYK-JS-OBJECTPATHSET-2388576
