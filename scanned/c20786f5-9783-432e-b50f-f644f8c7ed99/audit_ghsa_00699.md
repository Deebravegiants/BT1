# [H] Information Exposure in Snyk Broker

## Summary
Severity: High
Advisory: GHSA-mgh5-4h95-qj4p
CVE: CVE-2020-7654
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-mgh5-4h95-qj4p
Type: github-advisory

## Affected
- npm: `snyk-broker` — affected >=0 <4.73.1

## Details
All versions of snyk-broker before 4.73.1 are vulnerable to Information Exposure. It logs private keys if logging level is set to DEBUG.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7654
- https://snyk.io/vuln/SNYK-JS-SNYKBROKER-570613
- https://updates.snyk.io/snyk-broker-security-fixes-152338
