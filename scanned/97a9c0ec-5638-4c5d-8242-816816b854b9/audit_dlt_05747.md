# [?] [experimental] Make the params patcher warn on negative integer overflows too

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-web3.js
Published: 2023-03-29
Source: https://github.com/solana-foundation/solana-web3.js/commit/79b95f7fb68abeb37b06db97af7e4ea0a36bb722
Type: security-commit

## Details
[experimental] Make the params patcher warn on negative integer overflows too
## Summary

The code that patches up the params on their way to the Solana RPC warns on positive integer overflows (numeric values larger than `Number.MAX_SAFE_INTEGER`) but not on negative values. This PR fixes that, and reorganizes the tests to test the correct features at the correct levels.

## Test Plan

```
pnpm test:unit:browser
pnpm test:unit:node
```
