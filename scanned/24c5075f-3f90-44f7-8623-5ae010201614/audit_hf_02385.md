# [H] Revisited Withdrawal Amount Calculation in MultiFeeDistribution::exit()

## Summary
Severity: High
Contest weight: 0.6248
Dataset id: 12867
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Radiant V2 protocol, the MultiFeeDistribution contract provides an incentive mechanism that rewards the staking of the supported stakingToken with certain reward tokens. In particular, one entry routine, i.e., exit(), is designed to withdraw the unlocked and locked earnings. While examining its logic, we observe its current implementation needs to be improved. To elaborate, we show below the related code snippet of the MultiFeeDistribution contract. Inside the exit() routine, the withdrawableBalance() is called (line 1013) to calculate the withdrawable earnings amount. Especially, its returned amount includes the unlocked earnings amount (i.e., bal.unlocked) (line 644). However, we observe the bal.unlocked is added to amount again inside the exit() routine (line 1018), which will result in unexpected earnings for the user. Given this, we suggest to remove the statement of amount = amount + bal.unlocked (line 1018).
```solidity
function exit(bool claimRewards) external override {
    address onBehalfOf = msg.sender;
    (uint256 amount, uint256 penaltyAmount, uint256 burnAmount) = withdrawableBalance(onBehalfOf);
    delete userEarnings[onBehalfOf];
    Balances storage bal = balances[onBehalfOf];
    amount = amount + bal.unlocked;
    bal.total = bal.total.sub(bal.unlocked).sub(bal.earned);
    bal.unlocked = 0;
    bal.earned = 0;
    _withdrawTokens(
        onBehalfOf,
        amount,
        penaltyAmount,
        burnAmount,
        claimRewards
    );
}

function withdrawableBalance(address user) public view returns (uint256 amount, uint256 penaltyAmount, uint256 burnAmount) {
    Balances storage bal = balances[user];
    uint256 earned = bal.earned;
    amount = bal.unlocked.add(earned).sub(penaltyAmount);
    return (amount, penaltyAmount, burnAmount);
}
```

## Recommendation
Correct the exit() implementation by properly calculating the withdraw amount.
