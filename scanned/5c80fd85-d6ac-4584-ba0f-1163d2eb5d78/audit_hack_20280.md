# [H] 5.2.6 Incorrect auction end validation inliquidatorNFTClaim().

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** CollateralToken.sol#L
**Description:** liquidatorNFTClaim()does the following check to recognize that Seaport auction has ended:

```
if (block.timestamp < params.endTime) {
//auction hasn't ended yet
revert InvalidCollateralState(InvalidCollateralStates.AUCTION_ACTIVE);
}
```
Here,paramsis completely controlled by users and hence to bypass this check, the caller can setparams.endTime
to be less thanblock.timestamp.
Thus, a possible exploit scenario occurs whenAstariaRouter.liquidate()is called to list the underlying asset
on Seaport which also setsliquidatoraddress. Then, anyone can callliquidatorNFTClaim()to transfer the
underlying asset toliquidatorby settingparams.endTime < block.timestamp.
**Recommendation:** The parameter passed toliquidatorNFTClaim()should be validated against the parameters
created for the Seaport auction. To do that:

- collateralIdToAuctionmapping which currently mapscollateralIdto a boolean value indicating an ac-
    tive auction, should instead map fromcollateralIdto Seaport order hash.
- All usages ofcollateralIdToAuctionshould be updated. For example,isValidOrder()andisVali-
    dOrderIncludingExtraData()should be updated:
       return
       - s.collateralIdToAuction[uint256(zoneHash)]
       + s.collateralIdToAuction[uint256(zoneHash)] == orderHash
         ? ZoneInterface.isValidOrder.selector
          : bytes4(0xffffffff);
- liquidatorNFTClaim()should verify that hash ofparamsmatches the value stored incollateralIdToAuc-
    tionmapping. This validates thatparams.endTimeis not spoofed.
**Astaria:** Fixed in PR 210.
**Spearbit:** Verified.
