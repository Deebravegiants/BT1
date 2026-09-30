# [C] Prototype Pollution in litespeed.js and appwrite/server-ce

## Summary
Severity: Critical
Advisory: GHSA-v9p9-535w-4285
CVE: CVE-2021-23682
CWE: CWE-1321
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-17
Source: https://github.com/advisories/GHSA-v9p9-535w-4285
Type: github-advisory

## Affected
- npm: `litespeed.js` — affected >=0 <0.3.12
- Packagist: `appwrite/server-ce` — affected >=0.12.0 <0.12.2
- Packagist: `appwrite/server-ce` — affected >=0 <0.11.1

## Details
This affects the package litespeed.js before 0.3.12; the package appwrite/server-ce from 0.12.0 and before 0.12.2, before 0.11.1. When parsing the query string in the getJsonFromUrl function, the key that is set in the result object is not properly sanitized leading to a Prototype Pollution vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23682
- https://github.com/appwrite/appwrite/pull/2778
- https://github.com/litespeed-js/litespeed.js/pull/18
- https://github.com/appwrite/appwrite/releases/tag/0.11.1
- https://github.com/appwrite/appwrite/releases/tag/0.12.2
- https://snyk.io/vuln/SNYK-JS-LITESPEEDJS-2359250
- https://snyk.io/vuln/SNYK-PHP-APPWRITESERVERCE-2401820
