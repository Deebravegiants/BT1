# [M] Revisited Logic of MultiFeeDistribution::withdraw()

## Summary
Severity: Medium
Contest weight: 0.4561
Dataset id: 13328
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the UWU protocol, the MultiFeeDistribution contract provides an incentive mechanism that rewards the staking of the supported stakingToken with certain reward tokens. In particular, one entry routine, i.e., withdraw(), is designed to claim the unlocked earned rewards. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the MultiFeeDistribution contract. By design, the mapping(address => LockedBalance[]) private userEarnings records the user's earned rewards. Inside the withdraw() routine, the claimable rewards are accumulated within the for loop (line 1178) while the locked rewards reach the unlocked time. After that, the total claimable rewards are transferred to the recipient (line 1186). However, we notice the bal.earned (saving the total earned rewards) is not updated accordingly, which makes it possible for the user to get more rewards. Given this, we suggest to improve the implementation as below: bal.earned = bal.earned.sub(amount) (line 1186).
```solidity
function withdraw() public {
    _updateReward(msg.sender);
    Balances storage bal = balances[msg.sender];
    uint earned = bal.earned;
    uint amount;
    if (earned > 0) {
        uint length = userEarnings[msg.sender].length;
        for (uint i = 0; i < length; i++) {
            uint earnedAmount = userEarnings[msg.sender][i].amount;
            if (earnedAmount == 0) continue;
            if (userEarnings[msg.sender][i].unlockTime > block.timestamp) {
                break;
            }
            amount = amount.add(earnedAmount);
            delete userEarnings[msg.sender][i];
        }
        if (userEarnings[msg.sender].length == 0) {
            delete userEarnings[msg.sender];
        }
    }
    if (amount > 0) {
        rewardToken.safeTransfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }
}
```

## Recommendation
Revisit the implementation of the above withdraw() routine.
