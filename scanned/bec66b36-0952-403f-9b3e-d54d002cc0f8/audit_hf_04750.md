# [M] Attackers can create positions that have no

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 22586
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no incentive to liquidate tiny positions, which may lead to insolvency
A well-funded attacker (e.g. a competing exchange) can create millions of positions where each position's total open notional (and thus the liquidation fee given when closing the position) is smaller than the gas cost required to liquidate it if there's a loss.
Lots of small losses are equivalent to one large loss, which will lead to bad debt that the exchange will have to cover in order to allow others to withdraw from the PnL pool
There is no minimum position size, and the liquidation incentive is based on the total open notional (average cost to open):
```solidity
// File: src/clearingHouse/LibLiquidation.sol : LibLiquidation.getPenalty()
/// @notice penalty = liquidatedPositionNotionalDelta * liquidationPenaltyRatio, shared by liquidator and protocol
/// liquidationFeeToLiquidator = penalty * liquidation fee ratio. the rest to the protocol
function getPenalty(
    MaintenanceMarginProfile memory self,
    uint256 liquidatedPositionSizeDelta
) internal view returns (uint256, uint256) {
    // reduced percentage = toBeLiquidated / oldSize
    // liquidatedPositionNotionalDelta = oldOpenNotional * percentage = oldOpenNotional * toBeLiquidated / oldSize
    // penalty = liquidatedPositionNotionalDelta * liquidationPenaltyRatio
    uint256 openNotionalAbs = self.openNotional.abs();
    uint256 liquidatedNotionalMulWad = openNotionalAbs * liquidatedPositionSizeDelta;
    uint256 penalty = liquidatedNotionalMulWad.mulWad(self.liquidationPenaltyRatio) / self.positionSize.abs();
    uint256 liquidationFeeToLiquidator = penalty.mulWad(self.liquidationFeeRatio);
    uint256 liquidationFeeToProtocol = penalty - liquidationFeeToLiquidator;
    return (liquidationFeeToLiquidator, liquidationFeeToProtocol);
}
```
Furthermore, even if somehow gas costs were free, the mulWad() used to calculate the penalty/fee rounds down the total penalty as well as the portion that the liquidator gets, so one-wei open notionals will have a penalty payment of zero to the liquidator

## Recommendation
Have a minimum total open notional for positions, to ensure there's a large enough fee to overcome liquidation gas costs. Also round up the fee
