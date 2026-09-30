# [M] Nil pointer dereference via malicious RPC message in github.com/ethereum/go-ethereum

## Summary
Severity: Medium
Advisory: GO-2021-0063
Aliases: CVE-2020-26264, GHSA-r33q-22hv-j29q
Package: github.com/ethereum/go-ethereum
Published: 2021-04-14
Source: https://osv.dev/vulnerability/GO-2021-0063
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.9.25

## Details
Due to a nil pointer dereference, a maliciously crafted RPC message can cause a panic. If handling RPC messages from untrusted clients, this may be used as a denial of service vector.

## References
- https://github.com/ethereum/go-ethereum/pull/21896
- https://github.com/ethereum/go-ethereum/commit/bddd103a9f0af27ef533f04e06ea429cf76b6d46
