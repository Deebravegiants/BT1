# [M] The withdrawal queue is only updated when the liquidity is added

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Sometimes when the amount of liquidity is not much higher than the number of tokens locked for the collateral, it's impossible to withdraw liquidity.  For a user that wants to withdraw liquidity, a withdrawal request is created. If the request can't be executed, it's added to the withdrawal queue, and the user needs to wait until there's enough collateral for withdrawal. There are potentially 2 ways to achieve that: either someone adds more liquidity or some existing policies expire.

Currently, the queue can only be cleared when the internal `_updateWithdrawalQueue ` function is called. And it is only called in one place while adding liquidity:


 **code/contracts/PolicyBook.sol:L276-L290**
 ```solidity
 function _addLiquidityFor(address _liquidityHolderAddr, uint256 _liquidityAmount, bool _isLM) internal {
   daiToken.transferFrom(_liquidityHolderAddr, address(this), _liquidityAmount);    
   
   uint256 _amountToMint = _liquidityAmount.mul(PERCENTAGE_100).div(getDAIToDAIxRatio());
   totalLiquidity = totalLiquidity.add(_liquidityAmount);
   _mintERC20(_liquidityHolderAddr, _amountToMint);
 
   if (_isLM) {
     liquidityFromLM[_liquidityHolderAddr] = liquidityFromLM[_liquidityHolderAddr].add(_liquidityAmount);
   }
 
   _updateWithdrawalQueue();
 
   emit AddLiquidity(_liquidityHolderAddr, _liquidityAmount, totalLiquidity);
 }
 ```

#### Recommendation

It would be better if the queue could be processed when some policies expire without adding new liquidity. For example, there may be an external function that allows users to process the queue.
