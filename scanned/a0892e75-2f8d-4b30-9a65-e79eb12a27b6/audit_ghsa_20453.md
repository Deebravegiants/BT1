# [M] Cross-Site Request Forgery (CSRF) in livehelperchat

## Summary
Severity: Medium
Advisory: GHSA-6jmh-9gqm-5xrx
CVE: CVE-2022-0226
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-26
Source: https://github.com/advisories/GHSA-6jmh-9gqm-5xrx
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.92

## Details
A CSRF issue is found in the audit configuration under settings. It was found that no CSRF token validation is getting done on the server-side. If we remove the CSRF token and keep the CSRF token field empty, the action is getting performed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0226
- https://github.com/livehelperchat/livehelperchat/commit/f59ffb02984c0ce2fbb19ac39365066507de9370
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/635d0abf-7680-47f6-a277-d9a91471c73f
