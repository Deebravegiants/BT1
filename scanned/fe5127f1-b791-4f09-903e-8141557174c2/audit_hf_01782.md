# [M] new deposits be incorrectly rejected due to false "maxCapReached" errors.

## Summary
Severity: Medium
Contest weight: 0.5955
Dataset id: 9805
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Once the vault is completely liquidated, totalDepositAmount remains unchanged. Even when the withdrawer(deposit) tries to withdraw, totalDepositAmount is not reduced by the depositInfo[depositId].amount.

As a result new deposits be incorrectly rejected due to false "maxCapReached" errors.

When the perpetualVault is completely liquidated in such a way the collateralToken in the position is 0, the currPositionKey is made 0 but the position remains open. code
```solidity
  function afterLiquidationExecution() external {
    if (msg.sender != address(gmxProxy)) {
      revert Error.InvalidCall();
    }

    depositPaused = true;
    uint256 sizeInTokens = vaultReader.getPositionSizeInTokens(curPositionKey);
    if (sizeInTokens == 0) {
      delete curPositionKey;
    }
    ....
  }
```
This allows the the vault to continue the other user Operations like withdraw() and also the deposit() when the owner disable the depositPaused.

Now when user executes withdraw, this code willl get executed.
```solidity
function _withdraw(uint256 depositId, bytes memory metadata, MarketPrices memory prices) internal {
    ....
    else if (curPositionKey == bytes32(0)) {    // vault liquidated
      _handleReturn(0, true, false);
    } 
    ....
}
```
Inside the _handleReturn() the amount to transfer is calculated as
```solidity
    else {
      uint256 balanceBeforeWithdrawal = collateralToken.balanceOf(address(this)) - withdrawn;
      amount = withdrawn + balanceBeforeWithdrawal * shares / totalShares;
    }
```
The balance of the contract would be 0 by this time. => amount = 0;

As a result the fun _transferToken() will not get executed and also the totalDepositAmount is never get reduced.

The totalDepositAmount will never get reduced once the vault is liquidated and users start withdrawing. Hence it always show the incorrect value after on.

New deposits be incorrectly rejected due to false "maxCapReached" errors.

Protocol accounting becomes inaccurate, making it difficult to track actual assets under management

## Recommendation
the line      totalDepositAmount -= depositInfo[depositId].amount; should be put outside the transferToken() function so that it will be executed whatsoever.

Another way is to delete the totalDepositAmount once the vault is completely liquidated.

Low Risk Findings
