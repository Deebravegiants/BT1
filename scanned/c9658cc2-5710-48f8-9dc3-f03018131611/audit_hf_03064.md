# [M] `Pool._amountToBin`

## Summary
Severity: Medium
Contest weight: 0.7760
Dataset id: 17318
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the internal helper function that converts an ERC‑20 amount plus fee into a bin‑scaled amount. When the protocol fee ratio is set to its maximum (100 %), the function adds an extra unit to the fee calculation because the conditional expression adds +1 after multiplying the fee basis by the fee ratio. As a result the returned bin amount is one unit larger than it should be, which makes the internal delta that updates the pool’s bin balances smaller than the actual deposited amount. This off‑by‑one error propagates to the balance‑update logic, causing the pool to record a lower inbound balance and a higher fee than intended. Users who deposit tokens may see their balance reduced or receive a smaller share when withdrawing, while the protocol may collect an unintended extra fee. The bug appears only when the protocol fee ratio equals the maximum scaling constant; in all other configurations the function behaves correctly. It was discovered during a static audit that compared the expected fee calculation with the implementation and noticed that the fee basis is incremented by one. The issue is subtle because the deviation is a single unit, which may be hidden by rounding or large transaction amounts, making it hard to detect in normal operation. The proper fix is to treat the maximum‑ratio case as a special branch that returns deltaInErc‑feeBasis without the extra +1, or to adjust the clipping logic so that no additional unit is added. This class of bug is an off‑by‑one arithmetic error in fee accounting that breaks the invariant that total inbound amount equals sum of user amount and protocol fee.

## Proof of Concept
`delta.deltaInBinInternal` is used to update the bin balances like this (`Pool.sol#L287-L293`).
```solidity
if (tokenAIn) {
    binBalanceA += delta.deltaInBinInternal.toUint128();
    binBalanceB = Math.clip128(binBalanceB, delta.deltaOutErc.toUint128());
} else {
    binBalanceB += delta.deltaInBinInternal.toUint128();
    binBalanceA = Math.clip128(binBalanceA, delta.deltaOutErc.toUint128());
}
```

As we can see here (`Pool.sol#L608-L611`), `_amountToBin()` is used to calculate `delta.deltaInBinInternal` from `deltaInErc` and `feeBasis`.
```solidity
uint256 feeBasis = Math.mulDiv(binAmountIn, fee, PRBMathUD60x18.SCALE - fee, true);
delta.deltaInErc = binAmountIn + feeBasis;
delta.deltaInBinInternal = _amountToBin(delta.deltaInErc, feeBasis);
delta.excess = swapped ? Math.clip(amountOut, delta.deltaOutErc) : 0;
```

With the above code, the protocol fee should be a portion of `feeBasis` and it is the same as `feeBasis` when `state.protocolFeeRatio = ONE_3_DECIMAL_SCALE`.

But when we check `_amountToBin()`, the actual protocol fee will be `feeBasis + 1` and `delta.deltaInBinInternal` will be less than its possible smallest value (= `binAmountIn`).
```solidity
function _amountToBin(uint256 deltaInErc, uint256 feeBasis) internal view returns (uint256 amount) { 
    amount = state.protocolFeeRatio != 0 ? Math.clip(deltaInErc, feeBasis.mul(uint256(state.protocolFeeRatio) * PROTOCOL_FEE_SCALE) + 1) : deltaInErc;
}
```

## Recommendation
We should modify `_amountToBin()` like below.
```solidity
function _amountToBin(uint256 deltaInErc, uint256 feeBasis) internal view returns (uint256 amount) { 
    if (state.protocolFeeRatio == ONE_3_DECIMAL_SCALE)
        return deltaInErc - feeBasis;

    amount = state.protocolFeeRatio != 0 ? Math.clip(deltaInErc, feeBasis.mul(uint256(state.protocolFeeRatio) * PROTOCOL_FEE_SCALE) + 1) : deltaInErc;
}
```
