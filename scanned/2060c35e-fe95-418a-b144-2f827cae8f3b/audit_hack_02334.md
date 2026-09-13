# [M] \[M05\] Unnecessary input parameters

## Summary
Severity: Medium
Source: https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SurplusAuctionHouse.sol#L379
Type: audit-issue

## Details
In some functions, input parameters have only one acceptable value. If the input parameter does not have this value, the function call will revert.

For example, in [SuplusAuctionHouse.increaseBidSize](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SurplusAuctionHouse.sol#L379), the input parameter [amountToBuy](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SurplusAuctionHouse.sol#L379) is needed. However, a [strict equality to bids\[id\].amountToSell is required](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SurplusAuctionHouse.sol#L384).

Additionally, in [StabilityFeeTreasury.pullFunds](https://github.com/reflexer-labs/geb/blob/072f00ebd61a6704d7de66fea688479ed97628c3/src/StabilityFeeTreasury.sol#L287), the `token` parameter is [required to be equal to systemCoin](https://github.com/reflexer-labs/geb/blob/072f00ebd61a6704d7de66fea688479ed97628c3/src/StabilityFeeTreasury.sol#L293).

[SurplusAuctionHouse.startAuction](https://github.com/reflexer-labs/geb/blob/261407b6b332c2063e4256aa5f9b223d52dad7e1/src/SurplusAuctionHouse.sol#L154) has the input parameter `initialBid`, but this is always `0` when the function is called from other parts of the code.

Consider removing these unnecessary input parameters, and instead enforcing these strict equalities within the function’s logic. This will improve user experience for publicly callable functions by lowering the likelihood of a transaction to revert, and simplifying the user interface. This will also assist auditors and future developers in understanding the intent of the code. If these input parameters are desired to be kept, consider explaining why in the docstrings for the function.

_**Update:** Acknowledged, and will not fix. Reflexer Labs’ statement for this issue:_

> Maker wanted a general interface for `increaseBidSize` and `startAuction` because they’re probably thinking about the future where the implementation may evolve so we’d like to keep them as they are right now. As for `StabilityFeeTreasury.pullFunds` we want to keep token because the `pullFunds(address dstAccount, address token, uint256 wad)` signature will be used in a second iteration of a treasury that can handle any type of token. This way we keep a shared interface.
