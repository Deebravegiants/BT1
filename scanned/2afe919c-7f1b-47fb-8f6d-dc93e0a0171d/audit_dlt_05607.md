# [?] core/txpool/blobpool: avoid possible zero index panic (#30430)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-09-14
Source: https://github.com/ethereum/go-ethereum/commit/0dd7e82c0aef3c27303b4a7b30016790dda949d4
Type: security-commit

## Details
core/txpool/blobpool: avoid possible zero index panic (#30430)

This situation(`len(txs) == 0`) rarely occurs, but if it does, it will
panic.

---------

Co-authored-by: Martin HS <martin@swende.se>
