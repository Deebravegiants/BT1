# [H] Inconsistent Interpretation of HTTP Requests in github.com/gin-gonic/gin

## Summary
Severity: High
Advisory: GHSA-h395-qcrw-5vmq
CVE: CVE-2020-28483
CWE: CWE-113, CWE-444
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-h395-qcrw-5vmq
Type: github-advisory

## Affected
- Go: `github.com/gin-gonic/gin` — affected >=0 <1.7.7

## Details
When gin is exposed directly to the internet, a client's IP can be spoofed by setting the X-Forwarded-For header. This affects all versions of package github.com/gin-gonic/gin under 1.7.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28483
- https://github.com/gin-gonic/gin/issues/2232
- https://github.com/gin-gonic/gin/issues/2473
- https://github.com/gin-gonic/gin/issues/2862
- https://github.com/gin-gonic/gin/pull/2474
- https://github.com/gin-gonic/gin/pull/2474#23issuecomment-729696437
- https://github.com/gin-gonic/gin/pull/2632
- https://github.com/gin-gonic/gin/pull/2675
- https://github.com/gin-gonic/gin/pull/2844
- https://github.com/gin-gonic/gin/pull/2844/files#diff-e6ce689a25eaef174c2dd51fe869fabbe04a6c6afbd416b23eda138c82e761baR1432
- https://github.com/gin-gonic/gin/commit/03e5e05ae089bc989f1ca41841f05504d29e3fd9
- https://github.com/gin-gonic/gin/commit/5929d521715610c9dd14898ebbe1d188d5de8937
- https://github.com/gin-gonic/gin/commit/bfc8ca285eb46dad60e037d57c545cd260636711
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGINGONICGIN-1041736
- https://pkg.go.dev/vuln/GO-2021-0052
- https://github.com/gin-gonic/gin/releases/tag/v1.7.7
- https://github.com/gin-gonic/gin/releases/tag/v1.7.0
- https://github.com/gin-gonic/gin
