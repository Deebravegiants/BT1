# [M] TwitterServer Cross-site Scripting via /histograms endpoint

## Summary
Severity: Medium
Advisory: GHSA-3mqv-8gxg-pfm4
CVE: CVE-2020-35774
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-3mqv-8gxg-pfm4
Type: github-advisory

## Affected
- Maven: `com.twitter:twitter-server_2.12` — affected >=0 <20.12.0

## Details
server/handler/HistogramQueryHandler.scala in Twitter TwitterServer (aka twitter-server) before 20.12.0, in some configurations, allows XSS via the /histograms endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35774
- https://github.com/twitter/twitter-server/commit/e0aeb87e89a6e6c711214ee2de0dd9f6e5f9cb6c
- https://advisory.checkmarx.net/advisory/CX-2020-4287
- https://github.com/twitter/twitter-server
- https://github.com/twitter/twitter-server/compare/twitter-server-20.10.0...twitter-server-20.12.0
