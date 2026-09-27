# [C] Prototype pollution vulnerability in 'predefine'

## Summary
Severity: Critical
Advisory: GHSA-mx3x-ghqm-r43h
CVE: CVE-2020-28280
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-mx3x-ghqm-r43h
Type: github-advisory

## Affected
- npm: `predefine` — affected >=0 <0.1.3

## Details
Prototype pollution vulnerability in 'predefine' versions 0.0.0 through 0.1.2 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28280
- https://github.com/bigpipe/predefine/commit/1a86a013c0b37c9d6ca078ba34017052af38b7fc
- https://github.com/bigpipe/predefine
- https://github.com/bigpipe/predefine/blob/238137e3d1b8288ff5d7529c3cbcdd371888c26b/index.js#L284
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28280
