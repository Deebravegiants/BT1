# [H] commitToLiens always reverts

## Summary
Severity: High
Contest weight: 0.2494
Dataset id: 17725
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function commitToLiens() always reverts at the call to _returnCollateral() which prevents borrowers from depositing collateral and requesting loans in the protocol. The collateral token with collateralId is already minted directly to the caller (i.e. borrower) in commitToLiens() at the call to _transferAndDepositAsset() function. That's because while executing _transferAndDepositAsset the NFT is transferred to COLLATERAL_TOKEN whose onERC721Received mints the token with collateralId to borrower (from address) and not the operator_ (i.e. AstariaRouter) because operator_ != from_. However, the call to _returnCollateral() in commitToLiens() incorrectly assumes that this has been minted to the operator and attempts to transfer it to the borrower which will revert because the collateralId is not owned by AstariaRouter as it has already been transferred/minted to the borrower. The function commitToLiens() always reverts, preventing borrowers from depositing collateral and requesting loans in the protocol, thereby failing to bootstrap its core NFT lending functionality.

## Recommendation
Remove the call to _returnCollateral() in commitToLiens().
