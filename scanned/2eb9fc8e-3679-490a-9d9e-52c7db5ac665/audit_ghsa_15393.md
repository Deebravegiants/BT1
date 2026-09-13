# [H] Server-Side Request Forgery in axios

## Summary
Severity: High
Advisory: GHSA-8hc4-vh64-cxmj
CVE: CVE-2024-39338
CWE: CWE-918
Ecosystem: npm
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-8hc4-vh64-cxmj
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.3.2 <1.7.4

## Details
axios 1.7.2 allows SSRF via unexpected behavior where requests for path relative URLs get processed as protocol relative URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39338
- https://github.com/axios/axios/issues/6463
- https://github.com/axios/axios/pull/6539
- https://github.com/axios/axios/pull/6543
- https://github.com/axios/axios/commit/6b6b605eaf73852fb2dae033f1e786155959de3a
- https://github.com/axios/axios
- https://github.com/axios/axios/releases
- https://github.com/axios/axios/releases/tag/v1.7.4
- https://jeffhacks.com/advisories/2024/06/24/CVE-2024-39338.html
