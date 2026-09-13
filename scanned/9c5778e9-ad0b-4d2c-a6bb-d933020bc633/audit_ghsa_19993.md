# [C] express-param vulnerable to Improper Handling of Extra Parameters

## Summary
Severity: Critical
Advisory: GHSA-fr54-72wr-cqvq
CVE: CVE-2017-20160
CWE: CWE-235
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-31
Source: https://github.com/advisories/GHSA-fr54-72wr-cqvq
Type: github-advisory

## Affected
- npm: `express-param` — affected >=0 <1.0.0

## Details
A vulnerability was found in flitto express-param up to 0.x. It has been classified as critical. This affects an unknown part of the file `lib/fetchParams.js`. The manipulation leads to improper handling of extra parameters. It is possible to initiate the attack remotely. Upgrading to version 1.0.0 can address this issue. The name of the patch is db94f7391ad0a16dcfcba8b9be1af385b25c42db. It is recommended to upgrade the affected component. The identifier VDB-217149 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20160
- https://github.com/flitto/express-param/pull/19
- https://github.com/flitto/express-param/commit/db94f7391ad0a16dcfcba8b9be1af385b25c42db
- https://github.com/flitto/express-param
- https://github.com/flitto/express-param/releases/tag/1.0.0
- https://vuldb.com/?ctiid.217149
- https://vuldb.com/?id.217149
