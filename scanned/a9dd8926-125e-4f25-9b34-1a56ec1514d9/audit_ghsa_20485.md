# [M] User enumeration in livehelperchat

## Summary
Severity: Medium
Advisory: GHSA-4xww-6h7v-29jg
CVE: CVE-2022-0083
CWE: CWE-209
Ecosystem: Packagist
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-4xww-6h7v-29jg
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.91

## Details
livehelperchat is vulnerable to Generation of Error Message Containing Sensitive Information. There is an observable discrepancy between errors generated for users that exist and those that do not.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0083
- https://github.com/livehelperchat/livehelperchat/commit/fbed8728be59040a7218610e72f6eceb5f8bc152
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/4c477440-3b03-42eb-a6e2-a31b55090736
