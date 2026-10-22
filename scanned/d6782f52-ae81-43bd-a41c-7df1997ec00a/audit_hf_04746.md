# [M] Loss of funds for trader because whitelisted

## Summary
Severity: Medium
Contest weight: 0.4613
Dataset id: 22581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation, a whitelisted maker cannot be liquidated, thus it can accumulate losses even after the available margin is exhausted. This leads to losses for the traders because they won't be able to close their profitable positions due to a revert on _checkMarginRequirement. Scenario:
1) A trader opens a long position against a whitelisted maker.
2) After some time, the price increases significantly. At this point, there are more long positions open than short positions, so this maker incurs large losses. The margin is not sufficient to cover them. However, the maker cannot be liquidated and continues to accumulate losses.
3) The trader decides to close their position and withdraw their profit. However, this cannot happen because the _closePositionFor function calls _checkMarginRequirement for the maker. vault.getFreeCollateralForTrade is < 0, leading to a revert. The trader cannot close their position. The only solution is for LPs to deposit additional collateral to cover the losses, but it doesn't make sense to deposit funds to cover losses.
4) The price decreases, and the trader loses their profit. Due to fees or a sudden price drop, the trader may also lose part of the margin. In the described circumstances, the trader takes the risk by opening a position, but there is no way to close it and withdraw the profit. Thus, instead of gaining from the winning position, they incur losses.
```solidity
{
    _deposit(marketId, taker1, 10000e6);
    vm.prank(taker1);
    clearingHouse.openPosition(
        IClearingHouse.OpenPositionParams({
            marketId: marketId,
            maker: address(maker),
            isBaseToQuote: false,
            isExactInput: false,
            amount: 1000 ether,
            deadline: block.timestamp,
            makerData: ""
        })
    );
    console.log("Pnl pool balance: %d", vault.getPnlPoolBalance(marketId));
    maker.setBaseToQuotePrice(111e18);
    maker2.setBaseToQuotePrice(111e18);
    _mockPythPrice(111, 0);
    console.log("getFreeCollateralForTrade:");
    console.logInt(vault.getFreeCollateralForTrade(marketId, address(maker), 111e18, MarginRequirementType.MAINTENANCE));
    vm.prank(taker1);
    clearingHouse.closePosition(
        IClearingHouse.ClosePositionParams({
            marketId: marketId,
            maker: address(maker),
            deadline: block.timestamp,
            makerData: ""
        })
    );
}
```
Loss of funds for the trader + broken core functionality because of inability to close a position.

## Recommendation
The best solution is to implement liquidation for whitelisted maker. If not possible, you can mitigate the issue with larger margin requirement for whitelisted makers.
