# [H] PerpDepository#getPositionValue uses incor-rect TWAP interval

## Summary
Severity: High
Contest weight: 0.5949
Dataset id: 19798
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PerpDepository#getPositionValue queries the exchange for the mark price to calculate the unrealized PNL. Mark price is defined as the 15 minute TWAP of the market. The issue is that it uses the 15 second TWAP instead of the 15 minute TWAP. Mark price is a 15 minute / 900 second TWAP.
```solidity
function getPositionValue() public view returns (uint256) {
    uint256 markPrice = getMarkPriceTwap(15);
    int256 positionSize = IAccountBalance(clearingHouse.getAccountBalance())
        .getTakerPositionSize(address(this), market);
    return markPrice.mulWadUp(_abs(positionSize));
}

function getMarkPriceTwap(uint32 twapInterval)
    public
    view
    returns (uint256)
{
    IExchange exchange = IExchange(clearingHouse.getExchange());
    uint256 markPrice = exchange
        .getSqrtMarkTwapX96(market, twapInterval)
        .formatSqrtPriceX96ToPriceX96()
        .formatX96ToX10_18();
    return markPrice;
}
```
As seen in the code above getPositionValue uses 15 as the TWAP interval. This means it is pulling a 15 second TWAP rather than a 15 minute TWAP as intended.
The mark price and by extension the position value will frequently be different from true mark price of the market allowing for larger rebalances than should be possible.

## Recommendation
I recommend pulling the TWAP fresh each time from ClearingHouseConfig, because the TWAP can be changed at anytime. If it is desired to make it a constant then it should at least be changed from 15 to 900.
