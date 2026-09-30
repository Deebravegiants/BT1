# [H] image-size: ICNS parser allows denial of service through an infinite loop

## Summary
Severity: High
Advisory: GHSA-w3rx-r6r6-pgpr
CVE: CVE-2025-71330
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-w3rx-r6r6-pgpr
Type: github-advisory

## Affected
- npm: `image-size` — affected >=0

## Details
image-size through 2.0.2 contains a denial of service vulnerability that allows remote attackers to permanently block the Node.js event loop by supplying a specially crafted ICNS image buffer. Attackers can craft an ICNS buffer containing valid magic bytes and a zero-valued entry length field to trigger an infinite loop in the ICNS parser, as the offset is never incremented when the entry length field is 0, causing the while loop condition to remain true indefinitely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-71330
- https://github.com/image-size/image-size
- https://joshua.hu/image-size-infinite-loop-dos-vulnerabilities
- https://web.archive.org/web/20260224152152/https://github.com/image-size/image-size/pull/439
- https://www.vulncheck.com/advisories/image-size-denial-of-service-via-malformed-icns-image-parsing
