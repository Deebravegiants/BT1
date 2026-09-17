# [M] Web Cache Poisoning in find-my-way

## Summary
Severity: Medium
Advisory: GHSA-jgrh-5m3h-9c5f
CVE: CVE-2020-7764
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-11-09
Source: https://github.com/advisories/GHSA-jgrh-5m3h-9c5f
Type: github-advisory

## Affected
- npm: `find-my-way` — affected >=0 <2.2.5
- npm: `find-my-way` — affected >=3.0.0 <3.0.5

## Details
This affects the package find-my-way before 2.2.5, from 3.0.0 and before 3.0.5. It accepts the Accept-Version' header by default, and if versioned routes are not being used, this could lead to a denial of service. Accept-Version can be used as an unkeyed header in a cache poisoning attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7764
- https://github.com/delvedor/find-my-way/commit/ab408354690e6b9cf3c4724befb3b3fa4bb90aac
- https://snyk.io/vuln/SNYK-JS-FINDMYWAY-1038269
- https://www.npmjs.com/package/find-my-way
