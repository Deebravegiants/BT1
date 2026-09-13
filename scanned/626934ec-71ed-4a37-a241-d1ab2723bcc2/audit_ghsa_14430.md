# [H] Prototype pollution in matrix-react-sdk 

## Summary
Severity: High
Advisory: GHSA-6g43-88cp-w5gv
CVE: CVE-2023-28103
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-03-29
Source: https://github.com/advisories/GHSA-6g43-88cp-w5gv
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=0 <3.69.0

## Details
### Impact
In certain configurations, data sent by remote servers containing special strings in key locations could cause modifications of the `Object.prototype`, disrupting matrix-react-sdk functionality, causing denial of service and potentially affecting program logic.

(This is part 2, where [CVE-2022-36060](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-36060) / [GHSA-2x9c-qwgf-94xr](https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-2x9c-qwgf-94xr) is part 1. Part 2 covers remaining vectors not covered by part 1, found in a codebase audit scheduled after part 1.)

### Patches
This is fixed in matrix-react-sdk 3.69.0

### Workarounds
None.

### References

- [Release blog post](https://matrix.org/blog/2023/03/28/security-releases-matrix-js-sdk-24-0-0-and-matrix-react-sdk-3-69-0)
- The advisory [GHSA-2x9c-qwgf-94xr](https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-2x9c-qwgf-94xr) ([CVE-2022-36060](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-36060)) refers to an initial set of vulnerable locations discovered and patched in matrix-react-sdk 3.53.0. We opted not to disclose that advisory while we performed an audit of the codebase and are now disclosing it jointly with this one.

### For more information
If you have any questions or comments about this advisory please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-2x9c-qwgf-94xr
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-6g43-88cp-w5gv
- https://nvd.nist.gov/vuln/detail/CVE-2023-28103
- https://github.com/matrix-org/matrix-react-sdk
- https://matrix.org/blog/2023/03/28/security-releases-matrix-js-sdk-24-0-0-and-matrix-react-sdk-3-69-0
