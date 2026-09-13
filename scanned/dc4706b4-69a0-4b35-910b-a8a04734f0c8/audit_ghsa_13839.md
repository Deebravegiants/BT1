# [H] is-url Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: High
Advisory: GHSA-p9w8-2mpq-49h9
CVE: CVE-2018-25079
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-04
Source: https://github.com/advisories/GHSA-p9w8-2mpq-49h9
Type: github-advisory

## Affected
- npm: `is-url` — affected >=0 <1.2.3

## Details
A vulnerability was found in Segmentio is-url up to 1.2.2. It has been rated as problematic. Affected by this issue is an unknown functionality of the file index.js. The manipulation leads to inefficient regular expression complexity. The attack may be launched remotely. Upgrading to version 1.2.3 is able to address this issue. The name of the patch is 149550935c63a98c11f27f694a7c4a9479e53794. It is recommended to upgrade the affected component. VDB-220058 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25079
- https://github.com/segmentio/is-url/pull/18
- https://github.com/segmentio/is-url/commit/149550935c63a98c11f27f694a7c4a9479e53794
- https://github.com/segmentio/is-url
- https://github.com/segmentio/is-url/releases/tag/v1.2.3
- https://vuldb.com/?ctiid.220058
- https://vuldb.com/?id.220058
