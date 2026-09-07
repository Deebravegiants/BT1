# [C] @acrontum/filesystem-template vulnerable to Command Injection due to fetchRepo API missing sanitization

## Summary
Severity: Critical
Advisory: GHSA-m2fc-9h5m-29cm
CVE: CVE-2022-21186
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-m2fc-9h5m-29cm
Type: github-advisory

## Affected
- npm: `@acrontum/filesystem-template` — affected >=0 <0.0.2

## Details
The package @acrontum/filesystem-template before 0.0.2 is vulnerable to Arbitrary Command Injection due to the fetchRepo API missing sanitization of the href field of external input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21186
- https://github.com/acrontum/filesystem-template/issues/13
- https://github.com/acrontum/filesystem-template/pull/14/commits/baeb727b60991ad82d9e63ac660883793abc0acc
- https://github.com/acrontum/filesystem-template/commit/baeb727b60991ad82d9e63ac660883793abc0acc
- https://github.com/acrontum/filesystem-template
- https://security.snyk.io/vuln/SNYK-JS-ACRONTUMFILESYSTEMTEMPLATE-2419071
