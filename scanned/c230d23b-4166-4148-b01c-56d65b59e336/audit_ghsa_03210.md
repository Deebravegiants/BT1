# [H] Path Traversal in browserless-chrome

## Summary
Severity: High
Advisory: GHSA-8p9r-f949-699g
CVE: CVE-2020-7758
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-8p9r-f949-699g
Type: github-advisory

## Affected
- npm: `browserless-chrome` — affected >=0 <1.43.0

## Details
This affects all versions of browserless-chrome before 1.43.0. User input flowing from the workspace endpoint gets used to create a file path filePath and this is fetched and then sent back to a user. This can be escaped to fetch arbitrary files from a server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7758
- https://github.com/browserless/chrome/commit/848b87e5bea4f8473eea85261a5ff922d6ebd2b6
- https://github.com/browserless/chrome
- https://github.com/browserless/chrome/blob/master/src/routes.ts%23L175
- https://github.com/browserless/chrome/releases/tag/1.40.2-chrome-stable
- https://snyk.io/vuln/SNYK-JS-BROWSERLESSCHROME-1023657
- https://www.npmjs.com/package/browserless-chrome
