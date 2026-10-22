# [H] Stuck Queued Withdrawal Caused By Incorrect Access Control

## Summary
Severity: High
Contest weight: 0.7740
Dataset id: 14449
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The call to DepositQueue::fillERC20withdrawBuffer() can only be called by RestakeManager and so will fail in OperatorDelegator::completeQueuedWithdrawal(), resulting in the withdrawal failing until the buﬀer is ﬁlled.
OperatorDelegator::completeQueuedWithdrawal() calls DepositQueue::fillERC20withdrawBuffer() if the WithdrawQueue has a positive buﬀer deﬁcit for all withdrawn tokens:
```solidity
// check if token is not Native ETH
if (address(tokens[i]) != IS_NATIVE) {
    // Check the withdraw buffer and fill if below buffer target
    uint256 bufferToFill = withdrawQueue.getBufferDeficit(address(tokens[i]));
    // get balance of this contract
    uint256 balanceOfToken = tokens[i].balanceOf(address(this));
    if (bufferToFill > 0) {
        bufferToFill = (balanceOfToken <= bufferToFill) ? balanceOfToken : bufferToFill;
        // update amount to send to the operator Delegator
        balanceOfToken -= bufferToFill;
        // safe Approve for depositQueue
        tokens[i].safeApprove(address(restakeManager.depositQueue()), bufferToFill);
        // fill Withdraw Buffer via depositQueue
        restakeManager.depositQueue().fillERC20withdrawBuffer(
            address(tokens[i]),
            bufferToFill
        );
    }
}
```
However, DepositQueue::fillERC20withdrawBuffer() has an onlyRestakeManager modiﬁer on it and cannot be called by any operator delegators:
```solidity
function fillERC20withdrawBuffer(
    address _asset,
    uint256 _amount
) external nonReentrant onlyRestakeManager {
```
Hence, withdrawals from EigenLayer for tokens that have a withdraw buﬀer deﬁcit in WithdrawQueue cannot be completed.
Restaking Smart Contract Review

## Recommendation
Consider changing the access control for DepositQueue::fillERC20withdrawBuffer() to allow calls from operator delegators.
