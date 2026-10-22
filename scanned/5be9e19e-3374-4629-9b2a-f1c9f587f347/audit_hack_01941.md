# [M] 5.2 Missing Slippage Protection

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Risk Accepted

The following functions do not guarantee any slippage protection for users and are thus susceptible for
front-running attacks:

- BancorPortal._uniV2RemoveLiquidity calls the functions removeLiqudity and
    removeLiquidityETH of UniswapV2Router02 with 1 wei slippage protection at all
    circumstances.
- BancorV1Migration.migratePoolTokens calls removeLiquidity in Bancor v1's
    StandardPoolConverter with 1 wei slippage protection at all circumstances.

Risk accepted:

The client accepts the risk, stating the following:

```
Similar to how liquidity removal is processed on these 3rd party protocols, it is assumed that users
will migrate their liquidity immediately and will be prompted with its results.
```
