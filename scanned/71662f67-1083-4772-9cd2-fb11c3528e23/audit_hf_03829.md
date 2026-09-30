# [M] Relying solely on oracle base slippage param-

## Summary
Severity: Medium
Contest weight: 0.4252
Dataset id: 20062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AaveLeverageStrategyExtension relies solely on oracle price data when determining the slippage parameter during a rebalance. This is problematic as chainlink oracles, especially mainnet, have upwards of 2% threshold before triggering a price update. If swapping between volatile assets, the errors will compound causing even bigger variation. These variations can be exploited via sandwich attacks.
AaveLeverageStrategyExtension.sol#L1147-L1152
```solidity
function _calculateMinRepayUnits(uint256 _collateralRebalanceUnits, uint256 _slippageTolerance, ActionInfo memory _actionInfo) internal pure returns (uint256) {

    return _collateralRebalanceUnits
        .preciseMul(_actionInfo.collateralPrice)
        .preciseDiv(_actionInfo.borrowPrice)
        .preciseMul(PreciseUnitMath.preciseUnit().sub(_slippageTolerance));
}
```
When determining the minimum return from the swap, _calculateMinRepayUnits the true value and the oracle value can be systematically exploited via sandwich attacks. Given the leverage nature of the module, these losses can cause significant loss to the pool.
Purely oracle derived slippage parameters will lead to significant and unnecessary losses

## Recommendation
The solution to this is straight forward. Allow keepers to specify their own slippage value. Instead of using an oracle slippage parameter, validate that the specified slippage value is a margin of (oracle - customSlippage) < threshold. This gives the best of both world. It allows for tighter and more reactive slippage controls while still preventing outright abuse in the event that the trusted keeper is compromised.
