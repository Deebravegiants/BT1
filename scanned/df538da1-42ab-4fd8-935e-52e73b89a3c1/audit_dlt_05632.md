# [?] rpc: fix non-deterministic error in eth_simulateV1 state override (#21382)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-24
Source: https://github.com/erigontech/erigon/commit/2d11f996c5e3da3ce0820fe3297611e8bf2ca9ff
Type: security-commit

## Details
rpc: fix non-deterministic error in eth_simulateV1 state override (#21382)

Sort override addresses once before both loops so map iteration order
never affects error messages or precompile-move semantics. Add nil guard
for precompiles map and test coverage for the MovePrecompileTo success
path.
Tests Re-enabled:
* eth_simulateV1/test_201 and 
* eth_createAccessList/test_15 (the code is already OK after PR #21086 )

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
