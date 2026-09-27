# [M] phin may include sensitive headers in subsequent requests after redirect

## Summary
Severity: Medium
Advisory: GHSA-x565-32qp-m3vf
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-x565-32qp-m3vf
Type: github-advisory

## Affected
- npm: `phin` — affected >=0 <3.7.1

## Details
### Impact

Users may be impacted if sending requests including sensitive data in specific headers with `followRedirects` enabled.

### Patches

The [follow-redirects](https://github.com/follow-redirects/follow-redirects) library is now being used for redirects and removes some headers that may contain sensitive information in some situations.

### Workarounds

N/A. Please update to resolve the issue.

## References
- https://github.com/ethanent/phin/security/advisories/GHSA-x565-32qp-m3vf
- https://github.com/ethanent/phin/commit/c071f95336a987dad9332fd388adeb249925cc57
- https://github.com/ethanent/phin
