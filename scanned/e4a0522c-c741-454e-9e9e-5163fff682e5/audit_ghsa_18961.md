# [M] body-parser is vulnerable to denial of service when url encoding is used

## Summary
Severity: Medium
Advisory: GHSA-wqch-xfxh-vrr4
CVE: CVE-2025-13466
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-wqch-xfxh-vrr4
Type: github-advisory

## Affected
- npm: `body-parser` — affected >=2.2.0 <2.2.1

## Details
### Impact

body-parser 2.2.0 is vulnerable to denial of service due to inefficient handling of URL-encoded bodies with very large numbers of parameters. An attacker can send payloads containing thousands of parameters within the default 100KB request size limit, causing elevated CPU and memory usage. This can lead to service slowdown or partial outages under sustained malicious traffic.

### Patches

This issue is addressed in version 2.2.1.

## References
- https://github.com/expressjs/body-parser/security/advisories/GHSA-wqch-xfxh-vrr4
- https://nvd.nist.gov/vuln/detail/CVE-2025-13466
- https://github.com/expressjs/body-parser/commit/b204886a6744b0b6d297cd0e849d75de836f3b63
- https://github.com/expressjs/body-parser
- https://github.com/expressjs/body-parser/releases/tag/v2.2.1
