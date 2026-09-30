# [H] Reentrancy during liquidation corrupts the LendingPool accounting completely

## Summary
Severity: High
Contest weight: 0.7589
Dataset id: 3039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Reentrancy in the liquidation process will corrupt the debt accounting by inflating the to-
talRealisedLiquidity variable and realisedLiquidityOf mapping.
The ongoing auctions count variable auctionsInProgress can get decremented more than once for
the same auction, locking the Junior Tranche forever.
LendingPool.skim() can be unavailable while there are no ongoing auctions and available during an
ongoing auction.

To participate in a liquidation auction, users must call Liquidator.bid() with the asset
amounts they wish to buy in return for repaying some of the debt.
During Liquidator.bid(), the debt repayment is handled through LendingPool.auctionRepay(), af-
ter which IAccount.auctionBid() is responsible for transferring the asked amounts of assets to the
bidding user.
The auction terminates if all of the debt is paid back during LendingPool.auctionRepay().
If the Account is back in an overcollateralized "healthy" state or all of the collateral is sold out or
block.timestamp > auctionInformation_.cutoffTimeStamp, the user could also pass true in the
endAuction_ variable and manually terminate ("settle") the auction.
An important detail is a separate Liquidator.endAuction() function that can be used to settle an
auction without purchasing collateral.

```solidity

## Recommendation
Add nonReentrant modifiers to AccountV1.auctionBid, AccountV1.endAuction(), and AccountV1.auctionBoughtIn().

```solidity
