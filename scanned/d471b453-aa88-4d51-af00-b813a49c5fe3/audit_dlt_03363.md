# [M] supplyTokenTo doesn't account for safeTransferFrom fees

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-07-pooltogether
Published: 2021-07-30
Source: https://github.com/code-423n4/2021-07-pooltogether-findings/issues/9
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
The function supplyTokenTo of MStableYieldSource retrieves the tokens from the msg.sender and deposits them.
However some tokens, like USDT might subtract a fee when transferring tokens. This means less tokens would be transferred than expected.

If this is not accounted for the MStableYieldSource contract would loose funds.

Note: other projects, like gro have special code for this situation:
https://github.com/code-423n4/2021-06-gro/blob/main/contracts/DepositHandler.sol#L146

## Proof of Concept
//https://github.com/pooltogether/pooltogether-mstable/blob/main/contracts/yield-source/MStableYieldSource.sol#L82
   function supplyTokenTo(uint256 mAssetAmount, address to) external override nonReentrant {
        mAsset.safeTransferFrom(msg.sender, address(this), mAssetAmount);
        uint256 creditsIssued = savings.depositSavings(mAssetAmount);
        imBalances[to] += creditsIssued;
        emit Supplied(msg.sender, to, mAssetAmount);
    }

## Tools Used

## Recommended Mitigation Steps
Change the code to something like:
   function supplyTokenTo(uint256 mAssetAmount, address to) external override nonReentrant {
        uint256 mAssetBalanceBefore = mAsset.balanceOf(address(this));   // remember balance before
        mAsset.safeTransferFrom(msg.sender, address(this), mAssetAmount);
        uint256 mAssetBalanceAfter = mAsset.balanceOf(address(this)); // check balance after
        uint256 mAssetsActual         = mAssetBalanceAfter - mAssetBalanceBefore;  // calculate difference
        uint256 creditsIssued           = savings.depositSavings(mAssetsActual); 
        imBalances[to] += creditsIssued;

        emit Supplied(msg.sender, to, mAssetAmount); // perhaps update the event to include mAssetsActual 

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-07-pooltogether-findings/issues/9_
