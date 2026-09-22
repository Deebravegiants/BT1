# [M] 5.3.9 CanceledSeaportauctions can still be claimed by the liquidator

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:**

- CollateralToken.sol#L263-L271
- AstariaRouter.sol#L696
**Description:** Canceled auctions can still be claimed by the liquidator
if (
s.idToUnderlying[collateralId].auctionHash !=
s.SEAPORT.getOrderHash(getOrderComponents(params, counterAtLiquidation))
) {
//revert auction params don't match
revert InvalidCollateralState(
InvalidCollateralStates.INVALID_AUCTION_PARAMS
);
}

If in the future we would add an authorised endpoint that could calls.SEAPORT.incrementCounter()to cancel
all outstanding NFT auctions, theliquidatorcan call this endpointliquidatorNFTClaim(..., counterAtLiq-
uidation)wherecounterAtLiquidationis the old counter to claim its NFT after the canceledSeaportauction
ends.
**Recommendation:** Make sure to use the currentSeaportcounter when authenticating an auction hash


```
if (
s.idToUnderlying[collateralId].auctionHash !=
s.SEAPORT.getOrderHash(getOrderComponents(params, s.SEAPORT.getCounter(address(this)))
) {
//revert auction params don't match
revert InvalidCollateralState(
InvalidCollateralStates.INVALID_AUCTION_PARAMS
);
}
```
**Astaria:** The goal was to allow the case where non cancelled auctions(expired) could be still retrieved, theres no
interest in incrementing nonces. Recommendation applied in PR 343.
**Spearbit:** Fixed.
