# [M] Arbitrary File Read in Snyk Broker

## Summary
Severity: Medium
Advisory: GHSA-4vj3-f849-5r48
CVE: CVE-2020-7653
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-4vj3-f849-5r48
Type: github-advisory

## Affected
- npm: `snyk-broker` — affected >=0 <4.80.0

## Details
All versions of snyk-broker before 4.80.0 are vulnerable to Arbitrary File Read. It allows arbitrary file reads for users with access to Snyk's internal network by creating symlinks to match whitelisted paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7653
- https://snyk.io/vuln/SNYK-JS-SNYKBROKER-570612
- https://updates.snyk.io/snyk-broker-security-fixes-152338
