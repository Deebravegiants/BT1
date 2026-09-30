# [M] `_deductFees`

## Summary
Severity: Medium
Contest weight: 0.5847
Dataset id: 21520
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the fee‑deduction routine that is shared by the V3Automation and V3Utils modules. The function calculates a fee for each token amount by multiplying the amount by a fixed‑point fee rate (feeX64) and then dividing by the Q64 scaling constant. Because the calculation uses integer division, any situation where 0 < feeX64 * amount < Q64 yields a feeAmount of zero after rounding down. The implementation, however, unconditionally invokes SafeERC20.safeTransfer to send the calculated fee to the fee taker, even when feeAmount is zero. Certain ERC20 tokens, such as those that explicitly revert on zero‑value transfers, cause the safeTransfer call to revert the entire transaction. Consequently, any operation that relies on _deductFees – including swaps, deposits, withdrawals, or automated actions – may fail unexpectedly when the fee rounds to zero for a supported token. From the user’s perspective the transaction simply reverts, often with an error like “transfer amount must be greater than zero”, leaving the user with no token movement and a perception that the protocol is broken or that their funds are stuck. The issue was discovered during a formal audit when the auditors observed that the fee calculation could produce zero and that the subsequent transfer was not guarded by a >0 check. It is subtle because the fee being zero is a mathematically valid outcome, yet the contract assumes a transfer will always succeed. The impact is medium: it does not lead to loss of funds, but it prevents legitimate interactions with the protocol for affected tokens, effectively denying service. The bug belongs to the class of “unchecked zero‑value external calls” or “zero‑transfer reverts”. To remediate, the contract should conditionally execute the fee transfer only when feeAmount > 0, as illustrated in the recommended code snippet, thereby aligning the business logic (charging a fee only when it is non‑zero) with the token’s transfer semantics and restoring expected behavior.

## Proof of Concept
In `Common._deductFees()`

```solidity
    if (params.feeX64 == 0) {
        revert NoFees();
    }

    if (params.amount0 > 0) {
        feeAmount0 = FullMath.mulDiv(params.amount0, params.feeX64, Q64);
        amount0Left = params.amount0 - feeAmount0;
        SafeERC20.safeTransfer(IERC20(params.token0), FEE_TAKER, feeAmount0);
    }
    if (params.amount1 > 0) {
        feeAmount1 = FullMath.mulDiv(params.amount1, params.feeX64, Q64);
        amount1Left = params.amount1 - feeAmount1;
        SafeERC20.safeTransfer(IERC20(params.token1), FEE_TAKER, feeAmount1);
    }
    if (params.amount2 > 0) {
        feeAmount2 = FullMath.mulDiv(params.amount2, params.feeX64, Q64);
        amount2Left = params.amount2 - feeAmount2;
        SafeERC20.safeTransfer(IERC20(params.token2), FEE_TAKER, feeAmount2);
    }
```

if `0 < params.feeX64 * params.amountX < Q64` then `feeAmountX = 0`. In this case the `SafeERC20.safeTransfer()` reverts on a token which reverts on zero transfers.

`_deductFees()` is used throughout the functionality of `V3Automation` and `V3Utils`.

## Recommendation
```solidity
if (feeAmount0 > 0) {
    SafeERC20.safeTransfer(IERC20(params.token0), FEE_TAKER, feeAmount0);
}
```

etc.
