# [H] Denial of Service in Go-Ethereum

## Summary
Severity: High
Advisory: GHSA-vmf7-hmh6-vv57
CVE: CVE-2022-23328
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-vmf7-hmh6-vv57
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0

## Details
A design flaw in all versions of Go-Ethereum allows an attacker node to send 5120 pending transactions of a high gas price from one account that all fully spend the full balance of the account to a victim Geth node, which can purge all of pending transactions in a victim node's memory pool and then occupy the memory pool to prevent new transactions from entering the pool, resulting in a denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23328
- https://dl.acm.org/doi/pdf/10.1145/3460120.3485369
- https://github.com/ethereum/go-ethereum
- https://tristartom.github.io/docs/ccs21.pdf
- http://ethereum.com
- http://go-ethereum.com
