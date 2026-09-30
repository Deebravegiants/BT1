# [H] Exchange Rate Manipulation From Operator-Initiated Undelegation

## Summary
Severity: High
Contest weight: 0.6354
Dataset id: 14461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The EigenLayer operator that all OperatorDelegator’s are delegated to can initiate queued withdrawals that forfeit all strategy tokens/ETH balances and hence, Renzo TVL staked in EigenLayer. This results in the lock up of funds and dramatically decreases the ezETH mint rate.
DelegationManager::undelegate() allows EigenLayer operators to undelegate a staker that is delegated to them. Doing so initiates a queued withdrawal on behalf of the staker for all shares in every strategy in EigenLayer.
Since this queued withdrawal is not executed through OperatorDelegator::queueWithdrawals(), the queuedShares mapping is not incremented and these withdrawals are not tracked, causing OperatorDelegator::getTokenBalanceFromStrategy() and OperatorDelegator::getStakedETHBalance() to return zero for every collateral token.
This results in a large amount of Renzo’s TVL being excluded from the accounting, which can be used to manipulate the ezETH/ETH mint rate to be very small, such that the malicious EigenLayer operator can deposit a very small amount of ETH or collateral tokens to mint a large amount of ezETH. A ﬂashloan can also be used to amplify the proﬁts from the exploit.
Furthermore, since queuedShares are not incremented during undelegation, the queued withdrawals cannot be completed as decrementing queuedShares in OperatorDelegator::completeQueuedWithdrawal() will cause an underﬂow error in line [282] below:
```solidity
for (uint256 i; i < tokens.length; ) {
    if (address(tokens[i]) == address(0)) revert InvalidZeroInput();
    // deduct queued shares for tracking TVL
    queuedShares[address(tokens[i])] -= withdrawal.shares[i];
}
```
This makes it impossible to recover the queued withdrawn TVL.

## Recommendation
To prevent ezETH/ETH mint rate manipulation from being exploited by externally queued withdrawals such as operator-initiated undelegations, the OperatorDelegator contract should keep track of DelegationManager’s cumulativeWithdrawalsQueued nonce for each OperatorDelegator. Both getTokenBalanceFromStrategy() and getStakedETHBalance() should revert if the OperatorDelegator and DelegationManager nonces are out of sync.
Keep in mind that these suggestions do not prevent the execution of the attack described above. However, they prevent the exploiter from proﬁting from the ezETH/ETH mint rate manipulation, as well as provide a way to recover from the Restaking Smart Contract Review attack by allowing an admin to recover withdrawn funds.
