# [M] LiquidityWarehouse::depositBorrower is susceptible

## Summary
Severity: Medium
Contest weight: 0.5949
Dataset id: 22616
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The first deposits made using LiquidityWarehouse::depositBorrower will be vulnerable to inflation attacks  
The LiquidityWarehouse abstract contract, which is inherited by both the OrangeLiquidityWarehouse and SteadefiLiquidityWarehouse contracts has a function called depositBorrower that currently looks like this:  
```solidity
function depositBorrower(uint256 depositAmount) external whenNotPaused nonReentrant {
    _compoundInterest();
    uint256 totalAssetAmount = getBorrowerNetAssetValue();
    _mint(
        msg.sender,
        BORROWER_LP_TOKEN_ID,
        _convertToShares(totalSupply(BORROWER_LP_TOKEN_ID), totalAssetAmount, depositAmount),
        bytes("")
    );
    s_terms.asset.safeTransferFrom(msg.sender, address(this), depositAmount);
    if (_isLiquidationThresholdFulfilled()) {
        _activate();
    }
    emit AssetDeposited(depositAmount, true);
}
```
It uses the LiquidityWarehouse::getBorrowerNetAssetValue function, in order to fetch the totalAssetAmount.  
```solidity
function getBorrowerNetAssetValue() public view returns (uint256) {
    return getNetAssetValue() - getLenderNetAssetValue();
}
```
As it can be seen, that function simply returns the difference between the netAssetValue and the lenderNetAssetValue. Since the netAssetValue is based on the total asset balance of the contract, this means that whenever some amount of assets is transferred to it in one way or another, the borrowerNetAssetValue will also increase.  
Finally, if we look at the LiquidityWarehouse::_convertToShares function that is used to determine the amount of shares to be minted, we can see that the amount of shares returned by it is based on the totalAssetAmount, which in our case is based on the contract balance of the particular asset, as we mentioned above.  
```solidity
function _convertToShares(uint256 totalShareAmount, uint256 totalAssetAmount, uint256 assetAmount)
    internal
    pure
    returns (uint256)
{
    if (totalShareAmount == 0) return assetAmount; // Handle case when no shares have been minted yet
    return assetAmount.wadMul(totalShareAmount).wadDiv(totalAssetAmount);
}
```
Taking all of those things into account, we come to the following conclusion - If a given user deposits an amount of assets that is less than the price per share, they will receive 0 shares in return. The problem with this is that it can easily be exploited when the first borrower deposit transaction is sent to the mempool, by performing a sandwich attack to it. And to showcase what is meant by that, let's take a look at an example:  
1. Bob sends a transaction to make a borrower deposit of 1000 USDC, which also just so happens to be the first borrower deposit made to that particular contract.  
2. Unfortunately for him, Alice has been carefully monitoring the mempool, so after she sees his transaction, she sandwiches it with two transactions of her own - a first one that makes a 1 USDC borrower deposit (which she receives 1 share for) and a second that directly transfers 1000 USDC to the contract (which brings up its borrower share price from 1 USDC to 1001 USDC).  
3. The transaction of Bob gets executed - He receives 0 borrower shares for his deposit, since the asset amount of it is less than the price per borrower share  
4. Alice executes another transaction that withdraws her 1 borrower share - She receives 2001 USDC minus a withdrawal fee  
The first users that deposit assets as a borrowers have a high likelihood of receiving no shares in return

## Recommendation
Revert when totalAssetAmount is equal to 0. Additionally, you might also want to use virtual shares / mint some amount of shares to the 0 address on the first deposit, in order to protect against partial inflation attacks.
