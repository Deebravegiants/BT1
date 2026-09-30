# [M] Centralization risks

## Summary
Severity: Medium
Contest weight: 0.4498
Dataset id: 5620
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Admin can allow new collateral wrappers using setCollateralWrapper function. This could bring centralization risk
1. Lets say Admin wants to prohibit auction of collateral X with token id Y.
2. Admin creates a malicious bundle and allows it using setCollateralWrapper function.
3. This malicious bundle always return collateral X with token id Y on calling enumerate function. Also on calling unwrap it does nothing.
4. Now Admin creates a NFT using this malicious bundle and calls liquidate function.
5. enumerate function is called which sets underlyingCollateralToken as X and underlyingCollateralTokenIds as Y.
```solidity
if (_collateralWrappers[collateralToken]) {
    /* Get underlying collateral token and underlying collateral token IDs */
    (underlyingCollateralToken, underlyingCollateralTokenIds) = ICollateralWrapper(collateralToken).enumerate(
        collateralTokenId,
        collateralWrapperContext
    );
}
```
6. This means Auction will get started on token id Y of X even though contract does not have this token.
7. Bidding will start and bidder fund will be locked.
8. Claim will fail since contract does not have the NFT.
9. So, bidder fund is stuck and if token id Y actually need to be placed for auction then it will fail since an auction is already in place.
Another way
1. Admin simply approves a malicious wrapper.
2. Admin mints himself a new bundle token with NFT X,Y,Z without actually passing these NFT.
3. Admin borrows and provide the bundle token from step2.
4. Borrow passes and Admin gets extra.
Another Instance: if Bot only calls withdrawCollateral on ExternalCollateralLiquidator.sol and liquidateCollateral is never called, this will mean collateral will be taken without paying any proceeds.

## Recommendation
_admin could be a multiSig so that instead of relying on a single owner, multiple parties must approve an operation. This can help reduce the risk. As communicated by product team, ExternalCollateralLiquidator is just for testing.
