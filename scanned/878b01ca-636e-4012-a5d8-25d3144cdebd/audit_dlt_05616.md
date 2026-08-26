# [?] rpc: fix eth_feeHistory panics for finalized/safe block markers (#23290)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-14
Source: https://github.com/erigontech/erigon/commit/958931e9977de020fb527fafbcc31a2c29b8f1bb
Type: security-commit

## Details
rpc: fix eth_feeHistory panics for finalized/safe block markers (#23290)

surfaced during glamsterdam-devnet-7 testing
we weren't correctly handling the special block markers representing
finalized/safe block markers which resulted in panics
