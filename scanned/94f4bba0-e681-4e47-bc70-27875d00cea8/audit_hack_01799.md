# [H] Liquidity withdrawal can be blocked

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The main problem in that issue is that the liquidity provider may face many potential issues when withdrawing the liquidity. Under some circumstances, a normal user will never be able to withdraw the liquidity. This issue consists of multiple factors that are interconnected and share the same solution.

* **There are no partial withdrawals when in the queue**.
When the withdrawal request is added to the queue, it can only be processed fully: 


   **code_new/contracts/PolicyBook.sol:L444-L451**
   ```solidity
   address _currentAddr = withdrawalQueue.head();
   uint256 _tokensToWithdraw = withdrawalsInfo[_currentAddr].withdrawalAmount;
   
   uint256 _amountInDAI = convertDAIXtoDAI(_tokensToWithdraw);
   
   if (_availableLiquidity < _amountInDAI) {
     break;
   }
   ```

   But when the request is not in the queue, it can still be processed partially, and the rest of the locked tokens will wait in the queue.


   **code_new/contracts/PolicyBook.sol:L581-L590**
   ```solidity
   } else if (_availableLiquidity < convertDAIXtoDAI(_tokensToWithdraw)) {
     uint256 _availableDAIxTokens = convertDAIToDAIx(_availableLiquidity);
     uint256 _currentWithdrawalAmount = _tokensToWithdraw.sub(_availableDAIxTokens);
     withdrawalsInfo[_msgSender()].withdrawalAmount = _currentWithdrawalAmount;
   
     aggregatedQueueAmount = aggregatedQueueAmount.add(_currentWithdrawalAmount);
     withdrawalQueue.push(_msgSender());
   
     _withdrawLiquidity(_msgSender(), _availableDAIxTokens);
   } else {
   ```
   
   If there's a huge request in the queue, it can become a bottleneck that does not allow others to withdraw even if there is enough free liquidity.

* **Withdrawals can be blocked forever by the bots**.

    The withdrawal can only be requested if there are enough free funds in the contract. But once these funds appear, the bots can instantly buy a policy, and for the normal users, it will be impossible to request the withdrawal. Even when a withdrawal is requested and then in the queue, the same problem appears at that stage.

* **The policy can be bought even if there are pending withdrawals in the queue**.

#### Recommendation

One of the solutions would be to implement the following changes, but the team should thoroughly consider them:

* Allow people to request the withdrawal even if there is not enough liquidity at the moment.
* Do not allow people to buy policies if there are pending withdrawals in the queue and cannot be executed.
* (Optional) Even when the queue is empty, do not allow people to buy policies if there is not enough liquidity for the pending requests (that are not yet in the queue).
* (Optional if the points above are implemented) Allow partial executions of the withdrawals in the queue.
