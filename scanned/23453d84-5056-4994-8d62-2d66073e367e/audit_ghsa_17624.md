# [M] taro-css-to-react-native Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f5xg-cfpj-2mw6
CVE: CVE-2025-5896
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-f5xg-cfpj-2mw6
Type: github-advisory

## Affected
- npm: `taro-css-to-react-native` — affected >=0 <4.1.2

## Details
A vulnerability was found in tarojs taro up to 4.1.1. It has been declared as problematic. This vulnerability affects unknown code of the file taro/packages/css-to-react-native/src/index.js. The manipulation leads to inefficient regular expression complexity. The attack can be initiated remotely. Upgrading to version 4.1.2 is able to address this issue. The name of the patch is c2e321a8b6fc873427c466c69f41ed0b5e8814bf. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5896
- https://github.com/NervJS/taro/pull/17619
- https://github.com/NervJS/taro/commit/c2e321a8b6fc873427c466c69f41ed0b5e8814bf
- https://github.com/NervJS/taro
- https://github.com/NervJS/taro/releases/tag/v4.1.2
- https://vuldb.com/?ctiid.311668
- https://vuldb.com/?id.311668
- https://vuldb.com/?submit.585796
