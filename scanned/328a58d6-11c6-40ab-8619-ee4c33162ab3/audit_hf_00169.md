# [H] Burning does not update reserves

## Summary
Severity: High
Contest weight: 0.5394
Dataset id: 919
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `ConcentratedLiquidityPool.burn` function sends out `amount0`/`amount1` tokens but only updates the reserves by decreasing it by the **fees of these amounts**.

```solidity
unchecked {
    // @audit decreases by fees only, not by amount0/amount1
    reserve0 -= uint128(amount0fees);
    reserve1 -= uint128(amount1fees);
}
```

This leads to the pool having wrong reserves after any `burn` action. The pool’s balance will be much lower than the reserve variables.

## Recommendation
The reserve should be decreased by what is transferred out. In `burn`’s case this is `amount0` / `amount1`.
