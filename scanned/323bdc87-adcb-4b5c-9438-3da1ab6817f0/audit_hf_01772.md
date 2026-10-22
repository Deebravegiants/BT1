# [M] User may withdraw more than expected if ADL event happens

## Summary
Severity: Medium
Contest weight: 0.5963
Dataset id: 9795
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
First, let's take a look at the action performed by Gamma when GMX's ADL (Automatic Deleveraging) invokes GmxProxy.sol's afterOrderExecution() callback:

```solidity
    } else if (msg.sender == address(adlHandler)) {
      uint256 sizeInUsd = dataStore.getUint(keccak256(abi.encode(positionKey, SIZEINUSD)));
      if (eventData.uintItems.items[0].value > 0) {
@-->    IERC20(eventData.addressItems.items[0].value).safeTransfer(perpVault, eventData.uintItems.items[0].value);
      }
      if (eventData.uintItems.items[1].value > 0) {
@-->    IERC20(eventData.addressItems.items[1].value).safeTransfer(perpVault, eventData.uintItems.items[1].value);
      }
@-->  if (sizeInUsd == 0) {
        IPerpetualVault(perpVault).afterLiquidationExecution();
      }
```

Any collateral & index tokens received from GMX are transferred to the PerpetualVault. And if this ADL has not resulted in the entire position size to be de-leveraged i.e. sizeInUsd > 0, then afterLiquidationExecution() is NOT called.

With that in mind, let's now look at a user's withdrawal flow:
User calls withdraw(). This sets flow = FLOW.WITHDRAW.
If there's an open position, calls _settle() which creates a GMX order.
GMX executes the settle order, triggering afterOrderExecution(). This sets nextAction = NextActionSelector.WITHDRAW_ACTION.
Keeper calls runNextAction() which if needed, swaps any indexTokens to collateralTokens.
Calls _withdraw() which creates a GMX decrease position order.
GMX executes decrease order, triggering afterOrderExecution(). This sets nextAction = NextActionSelector.FINALIZE.
Keeper calls runNextAction() which calls finalize() which calls handleReturn() to process the withdrawal.

However, finalize() and handleReturn() rely on contract's collateral token balance to determine how much withdrawn amount is to be credited back to the user. If an ADL inadvertently happens between steps 6 and 7, i.e. Keeper's runNextAction() gets front-runned coincidentally in the same block (Or Keeper fails to notice the ADL event and calls runNextAction() anyway), then user receives more than they should:

```solidity
  function _finalize(bytes memory data) internal {
    if (flow == FLOW.WITHDRAW) {
      (uint256 prevCollateralBalance, bool positionClosed, bool refundFee) = abi.decode(data, (uint256, bool, bool));
      // @audit : collateralToken balance has already increased due to ADL, inflating the withdrawn figure
@->   uint256 withdrawn = collateralToken.balanceOf(address(this)) - prevCollateralBalance;
      _handleReturn(withdrawn, positionClosed, refundFee);
    } else {
      delete swapProgressData;
      delete flowData;
      delete flow;
    }
  }

  function _handleReturn(uint256 withdrawn, bool positionClosed, bool refundFee) internal {
    (uint256 depositId) = flowData;
    uint256 shares = depositInfo[depositId].shares;
    uint256 amount;
    if (positionClosed) {
      amount = collateralToken.balanceOf(address(this)) * shares / totalShares;
    } else {
      // @audit-info : this is correctly calculated since both collateralTokenBalance and withdrawn are inflated by an equal degree  
@->   uint256 balanceBeforeWithdrawal = collateralToken.balanceOf(address(this)) - withdrawn; 
      // @audit : but this results in inflated amount due to inflated withdrawn
@->   amount = withdrawn + balanceBeforeWithdrawal * shares / totalShares; 
    }
    if (amount > 0) {
@->   _transferToken(depositId, amount); // @audit : user credited more than their fair share
    }
    // ... Rest of the code
```

User will receive both their proportional share from the decrease order AND the ADL tokens
This is incorrect since ADL tokens should be distributed across all position holders. Essentially, other position holders take a loss.

## Recommendation
The fix may not be quite that simple. We may need to properly track credited tokens during ADL, perhaps by having ADL tokens flow into a separate accounting bucket.

Another way could be to increment prevCollateralBalance inside the if (msg.sender == address(adlHandler)) branch when afterOrderExecution() callback happens.
