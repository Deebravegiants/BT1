# [H] liquidationAccountant can be claimed at any

## Summary
Severity: High
Contest weight: 0.8812
Dataset id: 17721
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
New liquidations are sent to the liquidationAccountant with a finalAuctionTimestamp value, but the actual value that is passed in is simply the duration of an auction. The claim() function uses this value in a require check, so this error will allow it to be called before the auction is complete. When a lien is liquidated, AstariaRouter.sol:liquidate() is called. If the lien is set to end in a future epoch, we call handleNewLiquidation() on the liquidationAccountant. One of the values passed in this call is the finalAuctionTimestamp, which updates the finalAuctionEnd variable in the liquidationAccountant. This value is then used to protect the claim() function from being called too early. However, when the router calls handleLiquidationAccountant(), it passes the
```solidity
LiquidationAccountant(accountant).handleNewLiquidation(
    lien.amount,
    COLLATERAL_TOKEN.auctionWindow() + 1 days
);
```
As a result, finalAuctionEnd will be set to 259200 (3 days). to be called:
```solidity
require(
    block.timestamp > finalAuctionEnd || finalAuctionEnd == uint256(0),
);
```
Because of the error above, block.timestamp will always be greater than finalAuctionEnd, so this will always be permitted. Anyone can call claim() before an auction has ended. This can cause many problems, but the clearest is that it can ruin the protocol's accounting by decreasing the Y intercept of the vault. For example, if claim() is called before the auction, the returned value will be 0, so the Y intercept will be decreased as if there was an auction that returned no funds.

## Recommendation
Adjust the call from the router to use the ending timestamp as the argument, rather than the duration:
```solidity
LiquidationAccountant(accountant).handleNewLiquidation(
    lien.amount,
    block.timestamp + COLLATERAL_TOKEN.auctionWindow() + 1 days
);
```
