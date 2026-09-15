# [H] static-dev-server vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-7fxm-c848-89q8
CVE: CVE-2022-25848
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-29
Source: https://github.com/advisories/GHSA-7fxm-c848-89q8
Type: github-advisory

## Affected
- npm: `static-dev-server` — affected 1.0.0

## Details
A path traversal vulnerability affects all versions of package static-dev-server. This is because when paths from users to the root directory are joined, the assets for the path accessed are relative to that of the root directory. There is currently no known workaround or fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25848
- https://gist.github.com/lirantal/5550bcd0bdf92c1b56fbb20e141fe5bd
- https://github.com/etoah/static-dev-server
- https://security.snyk.io/vuln/SNYK-JS-STATICDEVSERVER-3149917
