# [H] tiny-json-http missing SSL certificate validation

## Summary
Severity: High
Advisory: GHSA-7h42-5vj2-cq39
CVE: CVE-2018-1000096
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-13
Source: https://github.com/advisories/GHSA-7h42-5vj2-cq39
Type: github-advisory

## Affected
- npm: `tiny-json-http` — affected >=1.0.1 <7.0.0

## Details
brianleroux tiny-json-http version all versions since commit [9b8e74a232bba4701844e07bcba794173b0238a8](https://github.com/brianleroux/tiny-json-http/commit/9b8e74a232bba4701844e07bcba794173b0238a8) (Oct 29 2016) contains a Missing SSL certificate validation vulnerability in The libraries core functionality is affected. that can result in Exposes the user to man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000096
- https://github.com/brianleroux/tiny-json-http/pull/15
- https://github.com/brianleroux/tiny-json-http/commit/3c1e36d8bef3ef5fd8e4447f816d5ffe2bfc3190
- https://github.com/advisories/GHSA-7h42-5vj2-cq39
- https://github.com/brianleroux/tiny-json-http
