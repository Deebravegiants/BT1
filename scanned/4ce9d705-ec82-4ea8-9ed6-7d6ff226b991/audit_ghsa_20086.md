# [M] Oils JS vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-v279-v2xm-whq9
CVE: CVE-2021-4260
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-v279-v2xm-whq9
Type: github-advisory

## Affected
- npm: `oils` — affected >=0 <8.0.0

## Details
A vulnerability was found in oils-js. This vulnerability affects unknown code of the file core/Web.js. The manipulation leads to open redirect and the attack can be initiated remotely. The name of the patch is fad8fbae824a7d367dacb90d56cb02c5cb999d42. It is recommended to apply a patch to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4260
- https://github.com/mannyvergel/oils-js/commit/fad8fbae824a7d367dacb90d56cb02c5cb999d42
- https://github.com/mannyvergel/oils-js
- https://vuldb.com/?id.216268
- https://web.archive.org/web/20211204010604/https://www.npmjs.com/package/oils
