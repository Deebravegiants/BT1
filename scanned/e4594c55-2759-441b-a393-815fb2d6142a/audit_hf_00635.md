# [C] C-01 | Collateral-Free Borrows

## Summary
Severity: Critical
Contest weight: 0.2481
Dataset id: 2143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently the borrow function is at risk of cross-contract reentrancy. Consider the following scenario: (1) ImpermaxV3Borrowable.borrow with borrowAmount > 0 with an NFTLP collateral that is enough to cover the borrow. (2) Callback impermaxV3Borrow is called before tokenId's borrow balance is updated. At this point in time, the account's borrowed is 0. (3) Call ImpermaxV3Collateral.redeem with percentage=1e18 to get back the NFTLP. This is still in the context of the callback. (4) require(IBorrowable(borrowable0).borrowBalance(tokenId) = 0 and require(IBorrowable(borrowable1).borrowBalance(tokenId) = 0 should pass successfully as the account wasn't updated yet. (5) Back in ImpermaxV3Borrowable.borrow, canBorrow would be called, but the NFTLP position still has enough liquidity to cover the borrow and the getPositionData function would still return the proper values, even if Alice now holds the NFT instead of the ImpermaxV3Collateral contract. (6) Ultimately, Alice borrowed a non-zero amount but also holds the entirety of her collateral NFTLP.

## Recommendation
Ensure the ImpermaxV3Collateral contract holds the NFTLP collateral when there is an active borrow.
