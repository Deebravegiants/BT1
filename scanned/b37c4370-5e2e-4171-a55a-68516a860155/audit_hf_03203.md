# [M] Transferring Ownership Might Break The Mar-

## Summary
Severity: Medium
Contest weight: 0.6893
Dataset id: 17784
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After the transfer of the market ownership, the market might stop working, and no one could purchase any bond token from the market leading to a loss of sale for the market makers. The callbackAuthorized mapping contains a list of whitelisted market owners authorized to use the callback. When the users call the purchaseBond function, it will check at Line 390 if the current market owner is still authorized to use a callback. Otherwise, the function will revert. A.sol#L379 File: BondBaseSDA.sol
```solidity
379: function purchaseBond(
380: uint256 id_,
381: uint256 amount_,
382: uint256 minAmountOut_
383: ) external override returns (uint256 payout) {
384: if (msg.sender != address(_teller)) revert Auctioneer_NotAuthorized();
385:
386: BondMarket storage market = markets[id_];
387: BondTerms memory term = terms[id_];
388:
389: // If market uses a callback, check that owner is still callback authorized
390: if (market.callbackAddr != address(0) && !callbackAuthorized[market.owner])
391: revert Auctioneer_NotAuthorized();
```
However, if the market owner transfers the market ownership to someone else. The market will stop working because the new market owner might not be on the list of whitelisted market owners (callbackAuthorized mapping). As such, no one can purchase any bond token. A.sol#L336 File: BondBaseSDA.sol
```solidity
336: function pushOwnership(uint256 id_, address newOwner_) external override {
337: if (msg.sender != markets[id_].owner) revert Auctioneer_OnlyMarketOwner();
338: newOwners[id_] = newOwner_;
339: }
```
After the transfer of the market ownership, the market might stop working, and no one could purchase any bond token from the market leading to a loss of sale for the market makers.

## Recommendation
Before pushing the ownership, if the market uses a callback, implement an additional validation check to ensure that the new market owner has been whitelisted to use the callback. This will ensure that transferring the market ownership will not break the market due to the new market owner not being whitelisted.
```solidity
function pushOwnership(uint256 id_, address newOwner_) external override {
    if (msg.sender != markets[id_].owner) revert Auctioneer_OnlyMarketOwner();
    if (markets[id_].callbackAddr != address(0) && !callbackAuthorized[newOwner_])
        revert newOwnerNotAuthorizedToUseCallback();
    newOwners[id_] = newOwner_;
}
```
