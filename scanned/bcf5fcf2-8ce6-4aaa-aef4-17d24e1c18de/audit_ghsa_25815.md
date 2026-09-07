# [H] Denial of service in go-ethereum

## Summary
Severity: High
Advisory: GHSA-vrcc-g6vj-mh5w
CVE: CVE-2021-42219
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-vrcc-g6vj-mh5w
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0

## Details
Go-Ethereum v1.10.9 was discovered to contain an issue which allows attackers to cause a denial of service (DoS) via sending an excessive amount of messages to a node. This is caused by missing memory in the component /ethash/algorithm.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42219
- https://docs.google.com/document/d/1dYFSpNZPC0OV-n1mMqdc269u9yYU1XQy/edit?usp=sharing&ouid=112110745137218798745&rtpof=true&sd=true
