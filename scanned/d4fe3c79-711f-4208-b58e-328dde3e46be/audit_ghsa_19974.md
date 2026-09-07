# [M] Json2html vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-79mp-cxp4-9p6r
CVE: CVE-2018-25053
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-79mp-cxp4-9p6r
Type: github-advisory

## Affected
- npm: `node-json2html` — affected >=0 <1.2.0

## Details
Json2html is a client side javascript HTML templating library with wrappers for both jQuery and Node.js. A vulnerability was found in moappi Json2html up to 1.1.x and classified as problematic. This issue affects some unknown processing of the file json2html.js. The manipulation leads to cross site scripting. The attack may be initiated remotely. Upgrading to version 1.2.0 can address this issue. The name of the patch is 2d3d24d971b19a8ed1fb823596300b9835d55801. The associated identifier of this vulnerability is VDB-216959.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25053
- https://github.com/moappi/json2html/commit/2d3d24d971b19a8ed1fb823596300b9835d55801
- https://github.com/moappi/json2html
- https://github.com/moappi/json2html/releases/tag/1.2.0
- https://vuldb.com/?ctiid.216959
- https://vuldb.com/?id.216959
