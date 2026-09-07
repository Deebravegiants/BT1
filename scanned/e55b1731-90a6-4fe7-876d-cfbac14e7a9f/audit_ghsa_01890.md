# [M] Open Redirect in oauth2_proxy

## Summary
Severity: Medium
Advisory: GHSA-jm34-xm8m-w958
CVE: CVE-2017-1000070
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-jm34-xm8m-w958
Type: github-advisory

## Affected
- Go: `github.com/bitly/oauth2_proxy` — affected >=0 <2.2.0

## Details
The Bitly oauth2_proxy in version 2.1 and earlier was affected by an open redirect vulnerability during the start and termination of the 2-legged OAuth flow. This issue was caused by improper input validation and a violation of RFC-6819

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000070
- https://github.com/bitly/oauth2_proxy/issues/228
- https://github.com/bitly/oauth2_proxy/pull/359
- https://github.com/bitly/oauth2_proxy/commit/289a6ccf463a425c7606178c510fc5eeb9c8b050
- https://tools.ietf.org/html/rfc6819#section-5.2.3.5
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2017-1000070
