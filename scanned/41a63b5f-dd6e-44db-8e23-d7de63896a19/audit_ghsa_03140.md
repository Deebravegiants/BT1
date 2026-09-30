# [C] Prototype Pollution in tiny-conf

## Summary
Severity: Critical
Advisory: GHSA-4q97-fh3f-j294
CVE: CVE-2020-7724
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-4q97-fh3f-j294
Type: github-advisory

## Affected
- npm: `tiny-conf` — affected >=0

## Details
All versions of package tiny-conf up to and including version 1.1.0 are vulnerable to Prototype Pollution via the set function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7724
- https://github.com/tiny-conf/tiny-conf/commit/1f7be78bc68927996647cd45b4367f8975a3ea05
- https://snyk.io/vuln/SNYK-JS-TINYCONF-598792
