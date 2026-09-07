# [H] Answer vulnerable to account takeover because password reset links do not expire

## Summary
Severity: High
Advisory: GHSA-j97g-77fj-9c4p
CVE: CVE-2023-1976
CWE: CWE-263
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-j97g-77fj-9c4p
Type: github-advisory

## Affected
- Go: `github.com/answerdev/answer` — affected >=0 <1.0.6

## Details
answerdev/answer is an open-source knowledge-based community software. Answer prior to 1.0.6 is vulnerable to account takeover because the password reset link does not expire.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1976
- https://github.com/answerdev/answer/commit/813ad0b9894673b1bdd489a2e9ab60a44fe990af
- https://github.com/answerdev/answer
- https://huntr.dev/bounties/469bcabf-b315-4750-b63c-82ac86d153de
