# [M] Unsafe cast in `getCollateralRatio`

## Summary
Severity: Medium
Contest weight: 0.4921
Dataset id: 18768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an unsafe type conversion performed in the library function that calculates the collateralisation ratio of the protocol. The function computes a 256‑bit intermediate value representing the ratio of total collateral to the amount of stablecoins issued, then casts this value directly to a 64‑bit unsigned integer without any overflow protection. When the amount of issued stablecoins is extremely small – for example a single wei – while the collateral amount is large, the intermediate ratio can exceed the maximum value representable by a uint64 (2^64‑1). Because the cast truncates the higher bits, the returned ratio is silently wrapped to an incorrect, often much smaller number or to the maximum sentinel value. This mis‑reporting can occur during the initial deployment phase or any situation where the protocol is under‑collateralised in the view calculation, and it may be amplified if the raw collateral balance is manipulated while the issued amount remains low. From a user’s perspective the front‑end may display a collateral ratio of zero or an implausibly low figure, contradicting the expectation that the protocol is safely over‑collateralised. Consequently, downstream logic that relies on this ratio – such as minting limits, liquidation triggers, or governance thresholds – may make erroneous decisions, potentially allowing the creation of excess stablecoins or preventing legitimate withdrawals. The issue was identified during a manual audit where the reviewer flagged an “unsafe cast” comment and traced the arithmetic path that could overflow. It is difficult to notice in normal operation because the overflow condition requires extreme parameter values that are rarely exercised in routine tests, and the view function does not revert on overflow, merely returning a truncated value. The recommended remediation is to replace the direct cast with a safe casting library that checks for overflow, or to keep the ratio in a larger integer type and only down‑cast after confirming the value fits within the target range. By ensuring the conversion is safe, the protocol preserves accurate accounting, maintains its collateral guarantees, and prevents user‑visible anomalies such as “funds disappear” or “ratio shows zero”.

## Proof of Concept
`getCollateralRatio()` outputs the collateral ratio using the total collaterals and issued agTokens.

```solidity
    // The `stablecoinsIssued` value need to be rounded up because it is then used as a divizer when computing
    // the amount of stablecoins issued
    stablecoinsIssued = uint256(ts.normalizedStables).mulDiv(ts.normalizer, BASE_27, Math.Rounding.Up);
    if (stablecoinsIssued > 0)
        collatRatio = uint64(totalCollateralization.mulDiv(BASE_9, stablecoinsIssued, Math.Rounding.Up)); //@audit unsafe cast
    else collatRatio = type(uint64).max;
```

Typically, the `collatRatio` should be around `BASE_9` but the ratio might be larger than `type(uint64).max` during the initial stage.

Furthermore, `totalCollateralization` is calculated using the [raw balance of collaterals](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L73) and it might be manipulated when [stablecoinsIssued](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L85) is not large.

Then [collatRatio](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L87) might be cast to the wrong value.

After all, `getCollateralRatio()` will return the wrong ratio and it will affect the protocol seriously.

## Recommendation
I think we should use the [SafeCast](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/facets/Swapper.sol#L9) library in [getCollateralRatio()](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/transmuter/libraries/LibGetters.sol#L87).

This seems hardly doable. Assuming there is 1 stablecoin issued (1e18), you’d need 1e28 collateral. Furthermore no impact is described: this would just break this view function. Overall I think Low severity is more appropriate

@Picodes - Although it’s an edge case, it’s likely to happen and `getCollateralRatio()` plays an important role in the protocol. Will keep as Medium.

To overflow the protocol would need to be 1 billion % over collateralise so it is not likely to happen.

As #9 shows, 1 USD is enough when `stablecoinsIssued = 1 wei`. I think it should be mitigated for safety.

PR: <https://github.com/AngleProtocol/angle-transmuter/commit/6f2ffcb1e89e3bba05c9aa2133ef94347aa42c28>  
Adds safeCast.
