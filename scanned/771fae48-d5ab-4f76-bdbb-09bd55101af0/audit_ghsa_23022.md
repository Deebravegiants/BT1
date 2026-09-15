# [H] Privilege Issues in jailed

## Summary
Severity: High
Advisory: GHSA-77m7-9wvw-87fx
CVE: CVE-2022-23923
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-77m7-9wvw-87fx
Type: github-advisory

## Affected
- npm: `jailed` — affected >=0

## Details
All versions of package jailed are vulnerable to Sandbox Bypass via an exported alert() method which can access the main application. Exported methods are stored in the application.remote object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23923
- https://github.com/asvd/jailed
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-2441254
- https://snyk.io/vuln/SNYK-JS-JAILED-2391490
