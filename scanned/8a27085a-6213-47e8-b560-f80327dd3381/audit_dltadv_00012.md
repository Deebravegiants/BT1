# [H] Denial of Service in Go-Ethereum

## Summary
Severity: High
Advisory: GHSA-pvx3-gm3c-gmpr
Aliases: CVE-2022-23327
Package: github.com/ethereum/go-ethereum
Published: 2022-03-05
Source: https://osv.dev/vulnerability/GHSA-pvx3-gm3c-gmpr
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected unspecified

## Details
A design flaw in Go-Ethereum 1.10.12 and older versions allows an attacker node to send 5120 future transactions with a high gas price in one message, which can purge all of pending transactions in a victim node's memory pool, causing a denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23327
- https://dl.acm.org/doi/pdf/10.1145/3460120.3485369
- https://github.com/ethereum/go-ethereum
- https://nrdax.com/techniques/NRDAX-T0156-mempool-pending-eviction-flood
- https://tristartom.github.io/docs/ccs21.pdf
