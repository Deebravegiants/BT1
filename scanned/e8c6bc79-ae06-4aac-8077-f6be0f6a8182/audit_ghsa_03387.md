# [H] LDAP Injection in is-user-valid

## Summary
Severity: High
Advisory: GHSA-22cm-3qf2-2wc7
CVE: CVE-2021-23335
CWE: CWE-74, CWE-90
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-22cm-3qf2-2wc7
Type: github-advisory

## Affected
- npm: `is-user-valid` — affected >=0

## Details
All versions of package is-user-valid are vulnerable to LDAP Injection which can lead to either authentication bypass or information exposure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23335
- https://snyk.io/vuln/SNYK-JS-ISUSERVALID-1056766
