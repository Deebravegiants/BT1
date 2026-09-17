# [M] OwnCast remote code execution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-392h-r46j-q24p
CVE: CVE-2023-46480
Ecosystem: Go
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-392h-r46j-q24p
Type: github-advisory

## Affected
- Go: `github.com/owncast/owncast` — affected >=0

## Details
An issue in OwnCast v.0.1.1 allows a remote attacker to execute arbitrary code and obtain sensitive information via the authHost parameter of the indieauth function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46480
- https://github.com/owncast/owncast
- https://github.com/shahzaibak96/CVE-2023-46480
