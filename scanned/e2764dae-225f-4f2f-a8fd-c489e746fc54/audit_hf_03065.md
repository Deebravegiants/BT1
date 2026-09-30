# [M] TWA update is not correct

## Summary
Severity: Medium
Contest weight: 0.5959
Dataset id: 17319
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the calculation of the time‑weighted average price (TWAP) that the pool updates on every swap. The contract builds the TWAP by adding a fractional component derived from the end square‑root price of the swap. In the current implementation the endSqrtPrice value is first passed through a clipping function before the division that produces the fractional part. The clipping function forces the value to stay within the lower tick bound, which makes the division result always positive. Consequently the endSqrtPrice can only increase the active tick and can never decrease it, even when the true price movement should pull the tick downward, a logical error that originates from using Math.clip on endSqrtPrice, a misuse that discards the sign of the price delta. An attacker can trigger the condition by performing a swap where tokenAIn is false, a sqrtPriceLimit is used, and there is a gap between price bins. By crafting the swap so that the real end price lies below the lower tick, the contract still adds a positive contribution to the TWAP, skewing the average price upward. The protocol then uses the distorted TWAP to decide how to move bins, causing bins to shift in the wrong direction. Users consequently receive trades at prices that are worse than expected, liquidity may be re‑allocated incorrectly, and the accounting assumptions of the pool (that the TWAP reflects the true time‑weighted price) are violated. From a user’s point of view the UI may show a normal price but the subsequent swap may return less token than anticipated or the pool may appear to lose balance. The issue appears only during swaps that update the TWAP; normal reads of the price do not reveal the problem, making it hard to notice without detailed audit. The flaw was discovered during a formal security audit where the auditor observed that the second term of the TWAP sum is always positive and therefore cannot contribute negatively to the active tick. To remediate the bug the clipping should be removed and the fractional component should be calculated directly from endSqrtPrice relative to the lower and upper tick bounds, preserving its sign. Additionally the log‑TWAP calculation for swaps that hit a sqrtPriceLimit must be corrected to handle gaps between bins accurately. Implementing these changes restores the intended behavior where the TWAP can move both up and down, aligning bin movement with the true market price and preventing mispricing or loss of funds.

## Proof of Concept
The protocol updates `twa` on every swap and uses that to decide how to move bins.

But in the function `swap()`, the delta’s `endSqrtPrice` can not contribute negatively to the `activeTick` because it is wrapped with a `clip()` function.
```solidity
// Pool.sol
if (amountOut != 0) {
    if (tokenAIn) {
        binBalanceA += delta.deltaInBinInternal.toUint128();
        binBalanceB = Math.clip128(binBalanceB, delta.deltaOutErc.toUint128());
    } else {
        binBalanceB += delta.deltaInBinInternal.toUint128();
        binBalanceA = Math.clip128(binBalanceA, delta.deltaOutErc.toUint128());
    }
    twa.updateValue(currentState.activeTick * PRBMathSD59x18.SCALE + int256(Math.clip(delta.endSqrtPrice, delta.sqrtLowerTickPrice).div(delta.sqrtUpperTickPrice - delta.sqrtLowerTickPrice)));//@audit second part of the sum is always positive, should contribute both ways
}
```

I believe `delta.endSqrtPrice` should contribute both ways to the `activeTick` and it is quite possible for the `endSqrtPrice` to be out of the range `(delta.sqrtLowerTickPrice, delta.sqrtUpperTickPrice)`. (In another report, I mentioned an issue of accuracy loss in the calculation of `endSqrtPrice`).

## Recommendation
I recommend changing the relevant line as below without using `clip()` so that the `endSqrtPrice` can contribute to the `twa` reasonably.
```solidity
twa.updateValue(currentState.activeTick * PRBMathSD59x18.SCALE + int256((delta.endSqrtPrice, delta.sqrtLowerTickPrice).div(delta.sqrtUpperTickPrice - delta.sqrtLowerTickPrice)));
```

The suggested mitigation is not correct, but this did alert us to a related issue in calculating the fractional part of the log TWAP when swap to `sqrtPriceLimit` is used for `tokenAIn=false` and when there is a gap between bins. In that case, the fractional part of the twap is not accurate. We will implement a fix.
