# [H] yapi disables TLS/SSL certificate validation via rejectUnauthorized: false in Axios HTTPS agent

## Summary
Severity: High
Advisory: GHSA-663h-2vr3-ghrj
CVE: CVE-2025-70058
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-663h-2vr3-ghrj
Type: github-advisory

## Affected
- npm: `yapi-vendor` — affected >=0

## Details
An issue pertaining to CWE-295: Improper Certificate Validation was discovered in YMFE yapi v1.12.0. The application disables TLS/SSL certificate validation by setting 'rejectUnauthorized': false in the HTTPS agent configuration for Axios requests

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70058
- https://gist.github.com/zcxlighthouse/11c53803faf23f607c2787c166e811d4
- https://github.com/YMFE
- https://github.com/YMFE/yapi
- https://github.com/YMFE/yapi/blob/59bade3a8a43e7db077d38a4b0c7c584f30ddf8c/common/postmanLib.js#L110
