# [M] Client-Side JavaScript Prototype Pollution in oro/platform

## Summary
Severity: Medium
Advisory: GHSA-jx5q-g37m-h5hj
CVE: CVE-2021-43852
CWE: CWE-1321, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-jx5q-g37m-h5hj
Type: github-advisory

## Affected
- Packagist: `oro/platform` — affected >=4.1.0 <4.1.14
- Packagist: `oro/platform` — affected >=4.2.0 <4.2.8

## Details
### Summary

By sending a specially crafted request, an attacker could inject properties into existing JavaScript language construct prototypes, such as objects. Later this injection may lead to JS code execution by libraries that are vulnerable to Prototype Pollution.

### Workarounds

Configure WAF to drop requests containing next strings: `__proto__` , `constructor[prototype]`, `constructor.prototype`

## References
- https://github.com/oroinc/platform/security/advisories/GHSA-jx5q-g37m-h5hj
- https://nvd.nist.gov/vuln/detail/CVE-2021-43852
- https://github.com/oroinc/platform/commit/62c26936b3adee9c20255dcd9f8ee5c299b464a9
- https://github.com/oroinc/platform
