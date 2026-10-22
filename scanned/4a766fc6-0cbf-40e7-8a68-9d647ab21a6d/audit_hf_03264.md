# [M] `settleAuction`

## Summary
Severity: Medium
Contest weight: 0.4332
Dataset id: 17906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic error in the settleAuction function that determines whether an auction can be settled. The function is supposed to revert when there is no active auction (collateralIdToAuction == 0) or when the underlying NFT is not owned by the clearing house. However the code uses a logical AND (&&) between the two checks and also uses a negated comparison, which means the revert is only triggered when both conditions are true simultaneously. Consequently, if an auction exists but receives no bids, the condition evaluates to false and the function proceeds to call ClearingHouse.safeTransferFrom, transferring the collateral to the clearing house without any payment. This allows an attacker or any caller to settle an empty auction and cause the collateral to be moved out of the user's control. The impact is that users may lose ownership of their NFT or see their collateral disappear without receiving any compensation. The bug manifests at the end of an auction when settleAuction is invoked, typically by anyone. It affects all participants who lock collateral in the protocol, including borrowers and lenders. The issue was discovered during a manual audit of the auction flow, where the conditional logic was compared against the intended specification and found to be inverted. Because the function does not emit an explicit error when no bid is present, the problem can be subtle and may only be observed when a user’s NFT is unexpectedly transferred after an auction with zero bids. The correct fix is to replace the && with a logical OR (||) and to ensure the ownership comparison uses equality rather than inequality, matching the intended guard: if (auctionId == 0 || owner != clearingHouse) revert. This restores the intended safety check and prevents unauthorized transfers. The vulnerability belongs to the class of improper conditional checks leading to authorization bypass, often referred to as “logic flaw in access control” or “incorrect auction settlement guard”. From a user perspective, the UI may show that an auction has ended, but the user’s balance shows the NFT is no longer in their wallet, and no refund or payment is recorded. Users expect the auction to either award the highest bid or revert if there are no bids; instead the contract silently moves the asset, violating the accounting assumptions of the protocol.

## Proof of Concept
settleAuction is called at the end of the auction and will check if the status is legal

```solidity
function settleAuction(uint256 collateralId) public {
  if (
    s.collateralIdToAuction[collateralId] == bytes32(0) &&
    ERC721(s.idToUnderlying[collateralId].tokenContract).ownerOf(
      s.idToUnderlying[collateralId].tokenId
    ) !=
    s.clearingHouse[collateralId]
  ) {
    revert InvalidCollateralState(InvalidCollateralStates.NO_AUCTION);
  }
```

This check seems to be miswritten，The normal logic would be

s.collateralIdToAuction[collateralId] == bytes32(0) || ERC721(s.idToUnderlying[collateralId].tokenContract).ownerOf(
      s.idToUnderlying[collateralId].tokenId
    ) == s.clearingHouse[collateralId]

This causes ClearingHouse.safeTransferFrom() to execute successfully even if there is no bid.

## Recommendation
function settleAuction(uint256 collateralId) public {
  if (
    s.collateralIdToAuction[collateralId] == bytes32(0) || 
    ERC721(s.idToUnderlying[collateralId].tokenContract).ownerOf(s.idToUnderlying[collateralId].tokenId
    ) == 
    s.clearingHouse[collateralId]
  ) {
    revert InvalidCollateralState(InvalidCollateralStates.NO_AUCTION);
  }

Keeping medium severity despite the lack of clear impact, the lack of clear impact being due to flaws in the flow before these lines.
