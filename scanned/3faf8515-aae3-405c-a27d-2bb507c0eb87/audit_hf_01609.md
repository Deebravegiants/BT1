# [M] TheAttackerCanPreventTheDepositFromReaching maxRaiseAmount

## Summary
Severity: Medium
Contest weight: 0.5795
Dataset id: 8644
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Leap.depositEth(), if the current deposit exceeds maxRaiseAmount, it will revert:
```solidity
// uncapped if set to 0 initially.
if (launchParams.maxRaiseAmount != 0) {
    if (totalRaised + _value > launchParams.maxRaiseAmount)
        // cannot raise more than the cap.
        revert Errors.ERR_MaximumDepositReached();
}
```
During the PHASE_DEPOSIT, deposit and withdraw do not require fees and lock time:
```solidity
// users can make a deposit and withdraw at any time with 0% fee
PHASE_DEPOSIT,
```
Therefore, the attacker can first deposit up to maxRaiseAmount and then withdraw, effectively blocking normal users from depositing at a low cost. Here’s an example:

1. Assume totalRaised=90, maxAllocation=10, and maxRaiseAmount=100.

2. Alice wants to deposit 10, which should normally succeed.

3. Bob monitors Alice’s request, deposits 10 before her deposit, and withdraws 10 after her deposit.

4. The final transaction execution order is:
   - Bob deposits 10: success
   - Alice deposits 10: revert, cannot raise more than the cap.
   - Bob withdraw 10: success

5. In the end, Bob prevents Alice’s deposit at a very low cost (gas + create bundle), thereby preventing the total raised amount from reaching maxRaiseAmount.

6. Although each user is limited by maxAllocation, the attacker can use multiple accounts to carry out the attack simultaneously. The more accounts used, the larger the deposit amount that can be blocked.

The attacker can prevent the deposit from reaching maxRaiseAmount, the more accounts used by the attacker, the larger the deposit amount that can be blocked.

## Recommendation
Add a lock-up period during PHASE_DEPOSIT to increase the attacker’s capital cost.
