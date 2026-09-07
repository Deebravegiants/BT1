# [M] Cross Site Scripting (XSS) Vulnerability in Fetlife rollout-ui gem

## Summary
Severity: Medium
Advisory: GHSA-5xq9-h3j2-jxvc
CVE: CVE-2023-25309
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-5xq9-h3j2-jxvc
Type: github-advisory

## Affected
- RubyGems: `rollout-ui` — affected >=0 <0.5.3

## Details
Cross Site Scripting (XSS) Vulnerability in Fetlife rollout-ui version 0.5, allows attackers to execute arbitrary code via a crafted url to the delete a feature functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25309
- https://github.com/fetlife/rollout-ui/pull/15
- https://github.com/fetlife/rollout-ui/commit/713d9c2edd4d7b0d8c287bea960d3c6bd2c5b306
- https://cxsecurity.com/issue/WLB-2023050012
- https://github.com/fetlife/rollout-ui
- https://github.com/fetlife/rollout-ui/releases/tag/v0.5.3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rollout-ui/CVE-2023-25309.yml
- https://packetstormsecurity.com/files/172185/Rollout-UI-0.5-Cross-Site-Scripting.html
