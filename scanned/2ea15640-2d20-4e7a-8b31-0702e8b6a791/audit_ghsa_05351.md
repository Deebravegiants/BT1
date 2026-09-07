# [H] image-size: JXL and HEIF parsers allow denial of service through infinite loops

## Summary
Severity: High
Advisory: GHSA-5p2g-fcmc-qvqq
CVE: CVE-2025-71329
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-5p2g-fcmc-qvqq
Type: github-advisory

## Affected
- npm: `image-size` — affected >=0

## Details
image-size through 2.0.2 contains a denial of service vulnerability that allows remote attackers to permanently block the Node.js event loop by supplying a specially crafted image buffer with a zero-valued size field in a recognized box-type. Attackers can trigger an infinite loop in the JXL or HEIF image parsers by providing a crafted image containing a box with a size of zero, causing the offset to never advance and permanently hanging the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-71329
- https://github.com/image-size/image-size
- https://joshua.hu/image-size-infinite-loop-dos-vulnerabilities
- https://web.archive.org/web/20260224152152/https://github.com/image-size/image-size/pull/439
- https://www.vulncheck.com/advisories/image-size-denial-of-service-via-infinite-loop-in-jxl-heif-parser
