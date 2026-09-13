# [M] Regular expression deinal of service in express-validators

## Summary
Severity: Medium
Advisory: GHSA-cf2x-rqc8-grfq
CVE: CVE-2020-7767
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-cf2x-rqc8-grfq
Type: github-advisory

## Affected
- npm: `express-validators` — affected >=0

## Details
All versions of package express-validators are vulnerable to Regular Expression Denial of Service (ReDoS) when validating specifically-crafted invalid urls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7767
- https://snyk.io/vuln/SNYK-JS-EXPRESSVALIDATORS-1017404
