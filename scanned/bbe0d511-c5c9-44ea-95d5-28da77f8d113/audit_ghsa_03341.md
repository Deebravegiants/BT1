# [H] Improper Authentication in react-adal

## Summary
Severity: High
Advisory: GHSA-7mpx-vg3c-cmr4
CVE: CVE-2020-7787
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-7mpx-vg3c-cmr4
Type: github-advisory

## Affected
- npm: `react-adal` — affected >=0 <0.5.1

## Details
This affects versions of react-adal < 0.5.1. It is possible for a specially crafted JWT token and request URL can cause the nonce, session and refresh values to be incorrectly validated, causing the application to treat an attacker-generated JWT token as authentic. The logical defect is caused by how the nonce, session and refresh values are stored in the browser local storage or session storage. Each key is automatically appended by ||. When the received nonce and session keys are generated, the list of values is stored in the browser storage, separated by ||, with || always appended to the end of the list. Since || will always be the last 2 characters of the stored values, an empty string ("") will always be in the list of the valid values. Therefore, if an empty session parameter is provided in the callback URL, and a specially-crafted JWT token contains an nonce value of "" (empty string), then adal.js will consider the JWT token as authentic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7787
- https://github.com/salvoravida/react-adal/pull/115
- https://github.com/salvoravida/react-adal/commit/74158dba1647b12fe96fa401e306a6287fe9e2a9
- https://snyk.io/vuln/SNYK-JS-REACTADAL-1018907
