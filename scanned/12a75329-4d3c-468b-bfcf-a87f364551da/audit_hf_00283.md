# [M] `sNOTE.sol#_mintFromAssets`

## Summary
Severity: Medium
Contest weight: 0.3879
Dataset id: 1439
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
BALANCER_VAULT.joinPool{value: msgValue}(
    NOTE_ETH_POOL_ID,
    address(this),
    address(this), // sNOTE will receive the BPT
    IVault.JoinPoolRequest(
        assets,
        maxAmountsIn,
        abi.encode(
            IVault.JoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT,
            maxAmountsIn,
            0 // Accept however much BPT the pool will give us
        ),
        false // Don't use internal balances
    )
);
```

The current implementation of `mintFromNOTE()` and `mintFromETH()` and `mintFromWETH()` (all are using `_mintFromAssets()` with `minimumBPT` hardcoded to `0`) provides no parameter for slippage control, making it vulnerable to front-run attacks.

## Recommendation
No recommendation
