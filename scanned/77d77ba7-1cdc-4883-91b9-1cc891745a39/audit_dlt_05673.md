# [?] core: nil-safe BlockChain.Config to fix typed-nil TestTransientStorageReset panic

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-05-13
Source: https://github.com/0xPolygon/bor/commit/1ab3db1bc0de44a35eaab69c88999ad25e4a31d4
Type: security-commit

## Details
core: nil-safe BlockChain.Config to fix typed-nil TestTransientStorageReset panic

chain_makers.AddTxWithVMConfig calls b.addTx(nil, …) which threads a
nil *BlockChain into NewEVMBlockContext as a ChainContext interface.
Go wraps the typed nil — the interface itself is non-nil but the
underlying pointer is — so the `if chain != nil` guard at evm.go:88
(added in 4765ad6 to handle TestProcessParentBlockHash's nil-interface
case) does not skip the chain.Config() call. That dispatches to
(*BlockChain).Config() on a nil receiver and panics on bc.chainConfig.

Failing tests on CI: TestTransientStorageReset and any other path that
reaches GenerateChain → BlockGen.AddTxWithVMConfig → NewEVMBlockContext.

Make Config() return nil on a nil receiver. The caller's existing
`cfg != nil && cfg.Bor != nil` check then routes to EthereumTransfer,
matching the behaviour for the nil-interface case.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
