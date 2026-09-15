# [M] Denial of Service in node-sass

## Summary
Severity: Medium
Advisory: GHSA-9v62-24cr-58cx
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-9v62-24cr-58cx
Type: github-advisory

## Affected
- npm: `node-sass` — affected >=3.3.0 <4.13.1

## Details
Affected versions of `node-sass` are vulnerable to Denial of Service (DoS). Crafted objects passed to the `renderSync` function may trigger C++ assertions in `CustomImporterBridge::get_importer_entry` and `CustomImporterBridge::post_process_return_value` that crash the Node process. This may allow attackers to crash the system's running Node process and lead to Denial of Service.


## Recommendation

Upgrade to version 4.13.1 or later

## References
- https://github.com/sass/node-sass/commit/338fd7a14d3b8bd374a382336df16f9c6792b884
- https://github.com/sass/node-sass
- https://www.npmjs.com/advisories/961
