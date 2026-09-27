# [H] ip SSRF improper categorization in isPublic

## Summary
Severity: High
Advisory: GHSA-2p57-rm9w-gvfp
CVE: CVE-2024-29415
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-2p57-rm9w-gvfp
Type: github-advisory

## Affected
- npm: `ip` — affected >=0

## Details
The ip package through 2.0.1 for Node.js might allow SSRF because some IP addresses (such as 127.1, 01200034567, 012.1.2.3, 000:0:0000::01, and ::fFFf:127.0.0.1) are improperly categorized as globally routable via isPublic. NOTE: this issue exists because of an incomplete fix for CVE-2023-42282.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29415
- https://github.com/indutny/node-ip/issues/150
- https://github.com/indutny/node-ip/pull/143
- https://github.com/indutny/node-ip/pull/144
- https://github.com/indutny/node-ip
- https://security.netapp.com/advisory/ntap-20250117-0010
