# [H] Type Confusion in LiveHelperChat

## Summary
Severity: High
Advisory: GHSA-5cmw-fhq9-8fhh
CVE: CVE-2022-1176
CWE: CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-5cmw-fhq9-8fhh
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.96

## Details
Live Helper Chat provides live support for your website. Loose comparison causes IDOR on multiple endpoints in LiveHelperChat prior to 3.96. There is a fix released in versions 3.96 and 3.97. Currently, there is no known workaround.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1176
- https://github.com/livehelperchat/livehelperchat/commit/72c0df160bfe9838c618652facef29af99392ce3
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/3e30171b-c9bf-415c-82f1-6f55a44d09d3
