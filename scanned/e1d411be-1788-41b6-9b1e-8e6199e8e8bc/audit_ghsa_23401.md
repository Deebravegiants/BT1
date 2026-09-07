# [M] QuickApps CMS Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-825g-f3g2-6vxf
CVE: CVE-2017-1000495
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-825g-f3g2-6vxf
Type: github-advisory

## Affected
- Packagist: `quickapps/cms` — affected >=0 <2.0.0

## Details
QuickApps CMS version 2.0.0 is vulnerable to Stored Cross-site Scripting in the user's real name field resulting in denial of service and performing unauthorised actions with an administrator user's account

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000495
- https://github.com/quickapps/cms/issues/183
- https://github.com/quickapps/cms/commit/7d648f21bd87af8263dcd6449f0946a2dd31348a
- https://github.com/quickapps/cms
