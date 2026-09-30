# [H] Wrong refundExecutionFee in _handleReturn

## Summary
Severity: High
Contest weight: 0.6376
Dataset id: 9773
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Refund execution fee logic within the _handleReturn function use the wrong argument which causes the execution fee being refunded to the wrong recipient.

Below is a snippet of the _handleReturn function from PerpetualVault.sol:

```solidity
/**
@notice this function is an end of withdrawal flow.
@dev should update all necessary global state variables
* @param withdrawn amount of token withdrawn from the position
@param positionClosed true when position is closed completely by withdrawing all funds, or false
   */
  function _handleReturn(uint256 withdrawn, bool positionClosed, bool refundFee) internal {
    (uint256 depositId) = flowData;
    uint256 shares = depositInfo[depositId].shares;
    uint256 amount;
    if (positionClosed) {
      amount = collateralToken.balanceOf(address(this)) * shares / totalShares;
    } else {
      uint256 balanceBeforeWithdrawal = collateralToken.balanceOf(address(this)) - withdrawn;
      amount = withdrawn + balanceBeforeWithdrawal * shares / totalShares;
    }
    if (amount > 0) {
      _transferToken(depositId, amount);
    }
    emit Burned(depositId, depositInfo[depositId].recipient, depositInfo[depositId].shares, amount);
    _burn(depositId);

    if (refundFee) {
      uint256 usedFee = callbackGasLimit * tx.gasprice;
      if (depositInfo[depositId].executionFee > usedFee) {
        try IGmxProxy(gmxProxy).refundExecutionFee(depositInfo[counter].owner, depositInfo[counter].executionFee - usedFee) {} catch {}
      }
    }

    // update global state
    delete swapProgressData;
    delete flowData;
    delete flow;
  }
```

In the if refundFee block, it performs a check on depositInfo[depositId].executionFee but then uses depositInfo[counter] when calling refundExecutionFee. counter is a state variable that only increment by 1 when there is a new deposit, while depositId comes from the flowData which is updated with the value of the intended deposit id of the user that requested withdrawal.

Consider this scenario:
User A deposits funds, the contract increments the counter to 1 and the contract assigns a deposit ID of 1. In the deposit record depositInfo[1], User A has an executionFee of 1 ETH.
Shortly after, User B deposits funds, and the contract increments the counter to 2, creating depositInfo[2] with an executionFee of 1.2 ETH.
User A initiates a withdrawal that triggers the _handleReturn function with depositId 1.
Inside _handleReturn, the function calculates usedFee (for example, 0.1 ETH) and checks that depositInfo[1].executionFee (1 ETH) is greater than usedFee.

   Intended Behavior: The refund should be calculated as 1 ETH - 0.1 ETH = 0.9 ETH and be sent to User A.

   Actual Behavior: Due to the bug, the refund call uses depositInfo[2] instead of depositInfo[1]. As a result, the function refunds 1.2 ETH - 0.1 ETH = 1.1 ETH to User B instead of refunding User A.

It is noteworthy that this function will only hit the refund logic if the owner need to change the flow state to WITHDRAW through the setVaultState function, because the only instance where handleReturn is called with the refundFee parameter set to true is in the runSwap function which can be called manually through the runNextAction function by the keeper.

Execution fee is refunded to the wrong user with the wrong amount.

## Recommendation
Replace depositInfo[counter] with depositInfo[depositId] in the refund fee block to ensure that the refund logic correctly references the intended deposit.
