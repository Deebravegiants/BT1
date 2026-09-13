# [H] Denial of service vulnerability exists in libxmljs

## Summary
Severity: High
Advisory: GHSA-773h-w45w-f2f9
CVE: CVE-2022-21144
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-773h-w45w-f2f9
Type: github-advisory

## Affected
- npm: `libxmljs` — affected >=0 <0.19.8

## Details
libxmljs provides libxml bindings for v8 javascript engine. This affects all versions of package libxmljs. When invoking the libxmljs.parseXml function with a non-buffer argument the V8 code will attempt invoking the .toString method of the argument. If the argument's toString value is not a Function object V8 will crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21144
- https://github.com/libxmljs/libxmljs/pull/594
- https://github.com/libxmljs/libxmljs/commit/2501807bde9b38cfaed06d1e140487516d91379d
- https://github.com/libxmljs/libxmljs
- https://snyk.io/vuln/SNYK-JS-LIBXMLJS-2348756
