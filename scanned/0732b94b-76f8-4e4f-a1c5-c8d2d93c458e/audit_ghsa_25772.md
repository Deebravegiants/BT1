# [H] Denial of Service in Go-Ethereum

## Summary
Severity: High
Advisory: GHSA-pvx3-gm3c-gmpr
CVE: CVE-2022-23327
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-pvx3-gm3c-gmpr
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0

## Details
A design flaw in Go-Ethereum 1.10.12 and older versions allows an attacker node to send 5120 future transactions with a high gas price in one message, which can purge all of pending transactions in a victim node's memory pool, causing a denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23327
- https://dl.acm.org/doi/pdf/10.1145/3460120.3485369
- https://github.com/ethereum/go-ethereum
- https://tristartom.github.io/docs/ccs21.pdf
