# [H] Go Ethereum Denial of Service

## Summary
Severity: High
Advisory: GHSA-9h4h-8w5p-f28w
Aliases: CVE-2018-19184, GO-2022-0814
Package: github.com/ethereum/go-ethereum
Published: 2021-06-29
Source: https://osv.dev/vulnerability/GHSA-9h4h-8w5p-f28w
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.8.14

## Details
`cmd/evm/runner.go` in Go Ethereum (aka geth) allows attackers to cause a denial of service (SEGV) via crafted bytecode.
### Specific Go Packages Affected
github.com/ethereum/go-ethereum/cmd/evm

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19184
- https://github.com/ethereum/go-ethereum/issues/18069
- https://github.com/ethereum/go-ethereum/commit/83e2761c3a13524bd5d6597ac08994488cf872ef
- https://github.com/ethereum/go-ethereum/commit/fb9f7261ec51e38eedb454594fc19f00de1a6834
