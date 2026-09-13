# [M] Answer vulnerable to Insertion of Sensitive Information Into Sent Data

## Summary
Severity: Medium
Advisory: GHSA-65v8-6pvw-jwvq
CVE: CVE-2023-1975
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-65v8-6pvw-jwvq
Type: github-advisory

## Affected
- Go: `github.com/answerdev/answer` — affected >=0 <1.0.8

## Details
answerdev/answer is an open-source knowledge-based community software. Answer prior to 1.0.8 does not strip EXIF geolocation data from user-uploaded logos. As a result, anyone can get sensitive information like a user's device ID, geolocation, system information, system version, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1975
- https://github.com/answerdev/answer/commit/ac3f2f047ee00b4edaea7530e570ab67ff87cd6a
- https://github.com/answerdev/answer
- https://huntr.dev/bounties/829cab7a-4ed7-465c-aa96-29f4f73dbfff
