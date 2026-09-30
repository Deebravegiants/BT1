# [H] Panic due to improper validation of RPC messages in github.com/ethereum/go-ethereum

## Summary
Severity: High
Advisory: GO-2021-0075
Aliases: CVE-2018-12018, GHSA-p5gc-957x-gfw9
Package: github.com/ethereum/go-ethereum
Published: 2021-04-14
Source: https://osv.dev/vulnerability/GO-2021-0075
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.8.11

## Details
Due to improper argument validation in RPC messages, a maliciously crafted message can cause a panic, leading to denial of service.

## References
- https://github.com/ethereum/go-ethereum/pull/16891
- https://github.com/ethereum/go-ethereum/commit/a5237a27eaf81946a3edb4fafe13ed6359d119e4
