# [C] json-logic-js Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-67j4-2mh6-8627
CVE: CVE-2021-4329
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-05
Source: https://github.com/advisories/GHSA-67j4-2mh6-8627
Type: github-advisory

## Affected
- npm: `json-logic-js` — affected >=0 <2.0.1

## Details
A vulnerability, which was classified as critical, has been found in json-logic-js 2.0.0. Affected by this issue is some unknown functionality of the file logic.js. The manipulation leads to command injection. Upgrading to version 2.0.1 is able to address this issue. The name of the patch is c1dd82f5b15d8a553bb7a0cfa841ab8a11a9c227. It is recommended to upgrade the affected component. VDB-222266 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4329
- https://github.com/jwadhams/json-logic-js/pull/98
- https://github.com/jwadhams/json-logic-js/commit/c1dd82f5b15d8a553bb7a0cfa841ab8a11a9c227
- https://github.com/jwadhams/json-logic-js
- https://github.com/pypa/advisory-database/tree/main/vulns/json-logic/PYSEC-2023-209.yaml
- https://vuldb.com/?ctiid.222266
- https://vuldb.com/?id.222266
