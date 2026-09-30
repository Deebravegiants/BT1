# [H] CollateralManager#commitCollateral can be abused by any caller

## Summary
Severity: High
Contest weight: 0.6058
Dataset id: 19954
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CollateralManager#commitCollateral has no access control, allowing users to freely add malicious tokens to any bid.
```solidity
// CollateralManager.sol#L117-L130
function commitCollateral(
    uint256 _bidId,
    Collateral[] calldata _collateralInfo
) public returns (bool validation_) {
    address borrower = tellerV2.getLoanBorrower(_bidId);
    (validation_, ) = checkBalances(borrower, _collateralInfo);
    if (validation_) {
        for (uint256 i; i < _collateralInfo.length; i++) {
            Collateral memory info = _collateralInfo[i];
            _commitCollateral(_bidId, info);
        }
    }
}
```
CollateralManager#commitCollateral has no access control and can be called by anyone on any bidID. This allows an attacker to front-run lenders and add malicious tokens to a loan right before it is filled.
1) A malicious user creates a malicious token that can be transferred once before being paused and returns uint256.max for balanceOf.
2) User A creates a loan for 10e18 ETH against 50,000e6 USDC at 10% APR.
3) User B decides to fill this loan and calls TellerV2#lenderAcceptBid.
4) The malicious user sees this and front-runs with a CollateralManager#commitCollateral call adding the malicious token.
5) Malicious token is now paused breaking both liquidations and fully paying off the loan.
6) Malicious user leverages this to ransom the locked tokens, unpausing when it is paid.
User can add malicious collateral to any bid they wish.

## Recommendation
Cause CollateralManager#commitCollateral to revert if called by anyone other than the borrower, their approved forwarder or TellerV2.
