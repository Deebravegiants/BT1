# [H] Prototype Pollution in deep-get-set

## Summary
Severity: High
Advisory: GHSA-85cp-p426-42f5
CVE: CVE-2020-7715
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-85cp-p426-42f5
Type: github-advisory

## Affected
- npm: `deep-get-set` — affected >=0 <1.1.1

## Details
All versions of package deep-get-set prior to version 1.1.1 are vulnerable to Prototype Pollution via the main function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7715
- https://github.com/acstll/deep-get-set/commit/a127e65bc77ff5707a6a103819e140d11475c5f4
- https://snyk.io/vuln/SNYK-JS-DEEPGETSET-598666
