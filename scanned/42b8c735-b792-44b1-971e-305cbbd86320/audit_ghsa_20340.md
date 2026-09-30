# [H] Unhandled crash in npm posix

## Summary
Severity: High
Advisory: GHSA-27mx-gchc-6xjp
CVE: CVE-2022-21211
CWE: CWE-252
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-27mx-gchc-6xjp
Type: github-advisory

## Affected
- npm: `posix` — affected >=0

## Details
This affects all versions of package posix. When invoking the toString method, it will fallback to 0x0 value, as the value of toString is not invokable (not a function), and then it will crash with type-check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21211
- https://github.com/ohmu/node-posix
- https://snyk.io/vuln/SNYK-JS-POSIX-2400719
