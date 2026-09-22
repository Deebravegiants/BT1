# [M] Answer vulnerable to Exposure of Sensitive Information Through Metadata

## Summary
Severity: Medium
Advisory: GHSA-8jg3-rx43-3fv4
CVE: CVE-2023-1974
CWE: CWE-1230
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-8jg3-rx43-3fv4
Type: github-advisory

## Affected
- Go: `github.com/answerdev/answer` — affected >=0 <1.0.8

## Details
answerdev/answer is an open-source knowledge-based community software. Answer prior to 1.0.8 may expose sensitive information, such as EXIF data and GPS coordatinates, via image metadata.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1974
- https://github.com/answerdev/answer/commit/ac3f2f047ee00b4edaea7530e570ab67ff87cd6a
- https://github.com/answerdev/answer
- https://huntr.dev/bounties/852781c6-9cc8-4d25-9336-bf3cb8ee3439
