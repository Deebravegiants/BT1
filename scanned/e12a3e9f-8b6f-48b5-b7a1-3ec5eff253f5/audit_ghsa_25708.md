# [H] Prototype Pollution in madlib-object-utils

## Summary
Severity: High
Advisory: GHSA-pfv6-prqm-85q8
CVE: CVE-2022-24279
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-16
Source: https://github.com/advisories/GHSA-pfv6-prqm-85q8
Type: github-advisory

## Affected
- npm: `madlib-object-utils` — affected >=0 <0.1.8

## Details
The package madlib-object-utils before version 0.1.8 is vulnerable to Prototype Pollution via the `setValue` method, as it allows an attacker to merge object prototypes into it. *Note:* This vulnerability derives from an incomplete fix of [CVE-2020-7701](https://security.snyk.io/vuln/SNYK-JS-MADLIBOBJECTUTILS-598676)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24279
- https://github.com/Qwerios/madlib-object-utils/commit/8d5d54c11c8fb9a7980a99778329acd13e3ef98f
- https://github.com/Qwerios/madlib-object-utils
- https://snyk.io/vuln/SNYK-JS-MADLIBOBJECTUTILS-2388572
