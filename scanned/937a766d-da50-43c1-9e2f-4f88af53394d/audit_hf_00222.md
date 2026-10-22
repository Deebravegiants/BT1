# [M] Dutch auction can be manipulated

## Summary
Severity: Medium
Contest weight: 0.3487
Dataset id: 1146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When malt is under-peg and the swing trader module do not have enough capital to buy back to peg, a Dutch auction is triggered to sell arb token. The price of the Dutch auction decrease linearly toward endprice until _endAuction() is called. <https://github.com/code-423n4/2021-11-malt/blob/c3a204a2c0f7c653c6c2dda9f4563fd1dc1cecf3/src/contracts/Auction.sol#L589>

_endAuction() is called in

1. When auction.commitments >= auction.maxCommitments

2. On stabilize() -> checkAuctionFinalization() -> _checkAuctionFinalization()

3. On stabilize() ->_startAuction() -> triggerAuction() -> _checkAuctionFinalization()

It is possible manipulate the dutch auction by preventing _endAuction() being called.

## Proof of Concept
Consider someone call purchaseArbitrageTokens with auction.maxCommitments minus 1 wei, `_endAuction` won’t be called because auction.commitments < auction.maxCommitments. Further purchase would revert because `purchaseAndBurn` (<https://github.com/code-423n4/2021-11-malt/blob/c3a204a2c0f7c653c6c2dda9f4563fd1dc1cecf3/src/contracts/Auction.sol#L184>) would likely revert since swapping 1 wei in most AMM will fail due to rounding error. Even if it does not revert, there is no incentive to waste gas to purchase 1 wei of token.

As such, the only way for the auction to finalize is to call stabilize(). However, this is not immediately possible because it require `block.timestamp >= stabilizeWindowEnd` where `stabilizeWindowEnd = block.timestamp + stabilizeBackoffPeriod` stabilizeBackoffPeriod is initially set to 5 minutes in the contract

After 5 minute, stabilize() can be called by anyone. By using this exploit, an attacker can guarantee he can purchase at (startingPrice+endingPrice)/2 or lower, given the default 10 minute auctionLength and 5 minute stabilizeBackoffPeriod. (unless a privileged user call stabilize() which override the stability window)

Also note that stabilize() might not be called since there is no incentive.

## Recommendation
1. Incentivize stabilize() or incentivize a permission-less call to _endAuction()
2. Lock-in auction price when user commit purchase

By purchasing all but 1 wei of arbitrageTokens, any caller can guarantee that the auction will offer the steepest discount.

This is caused by the fact that AMMs (esp UniV2) will revert with small numbers, as rounding will cause the amountOut to == 0 which will cause a INSUFFICIENT_AMOUNT revert.

I agree with the pre-conditions and the possibility of this to happen. In a sense I believe this can become the meta strategy that every dutch auction participant will use (the fight between buyers will be done by paying gas to be the first few to buy arbitrageTokens).

So the question is how to avoid it. I guess purchasing at a time should lock the price for that particular buyer at that particular time (adding a mapping should increase cost of 20k on write and a few thousand gas on read).

TODO: Decide on severity

Medium for sure, extract value reliably. Is it high though? Arguably the dutch auction is not properly coded as it allows to get a further discount instead of locking in a price for the user at time of deposit

While an argument for the Dutch Auction being coded wrong (user locking in price) can be made, that’s not the definition of a Dutch Auciton

![Screenshot 2022-01-26 at 14 16 34](https://user-images.githubusercontent.com/13383782/151169628-a1d8e7e7-15c2-4064-a985-9f923154170a.png) https://www.investopedia.com/terms/d/dutchauction.asp 

So arguably the dutch auction is properly coded, it’s that there’s a specific way to sidestep it which is caused by:

* 1 wei tx reverting on swap
* sum of purchases not being enough


For this conditions to happen the “exploiter” needs to be fast enough to place an order, in such a way that their order will leave 1 commitment left. I can imagine them setting up a contract that reverts if this condition isn’t met and that checks for w/e amount is needed at that time.

I would assume that having an admin privileged function to close the auction prematurely would solve this specific attack.

I believe that the warden has identified a fairly reliable way to get a discount from the protocol because of the impact and some of the technicalities I believe Medium Severity to be more appropriate. This will be exploited, but in doing so will make the protocol successful (all auction full minus 1 wei), the premium / discount will be reliable predicted (50% between start and end) and as such I believe it will be priced in
