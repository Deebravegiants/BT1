# [M] A user can avoid paying fees in

## Summary
Severity: Medium
Contest weight: 0.4590
Dataset id: 1952
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to precision loss in the fees calculation a user will be able to avoid fees by splitting their withdraw into multiple smaller amounts
```solidity
function requestWithdraw(uint256 _amount, address _tranche) external returns (uint256) {
    ...
    uint256 _underlyings = _amount * _tranchePrice(_tranche) / ONE_TRANCHE_TOKEN;
    ...
    uint256 interest = _calcInterestWithdrawRequest(_underlyings) * _trancheAprRatio(_tranche) / FULL_ALLOC;
    uint256 fees = interest * fee / FULL_ALLOC;
    uint256 netInterest = interest - fees;
    ...
}
```
In the requestWithdraw function above we can see that the user will specify the amount of funds they are withdrawing. After that their portion of the interest is computed based on the specified amount. Then the fees are taken as a percentage of this amount.
However the issue is that if a user specifies a small enough amount that will gain interest, then the fees from that interest will be rounded down to 0. By splitting their withdraw into multiple smaller amounts they will be able to avoid paying the fees. When we look into the contest readMe we can see that tokens with 6 decimals will be supported:
Standard ERC20 tokens + USDT with no less than 6 decimals and no more than 18 decimals. Rebasing tokens, fee-on-transfer tokens, and tokens with multiple entry points are NOT supported. And also the contract will be deployed on Optimism and other L2s which has extremely low transaction fees. This attack will cause even bigger loss for the protocol with tokens that have 6 decimals and have a huge value.
Internal Pre-conditions
1. The contract is deployed on an L2(eg. Optimism which is allowed by the readMe)
2. The contract will use tokens with less than 8 decimals(eg. wbtc). In the readMe it is specified that standard tokens with 6 to 18 decimals will be supported.
External Pre-conditions
N/A
Attack Path
Consider the following scenario: The attacker wants to withdraw 0.01WBTC which is equal to 1e6 (around 1000$ of value). Expected fee is (10%*4%*1e6) = 4e3WBTC=4$ The interest that the attacker will gain is 4% and the fee is 10% In order for the attack to be profitable the 10% of the gained interest shall be rounded down to 0 here: racts/IdleCDOEpochVariant.sol#L519 which means that the interest for a single transaction shall be less than 9 wei so that the fees will round down to 0. In order for the interest to be 9 wei the total withdrawn amount shall be 225 wei for a transaction.(which is 0.225).Placingthisinalooptheattackerwillrunitmultipletimeswhichwillcostlessthan1 in total on optimism as transaction fees are extremely small(even negligible). As a result the fee will go to the attacker leading to a loss of the whole fee of the withdraw for the protocol.
On L2 the attack will be very cheap and will be profitable for the attacker, especially for big amounts. Loss of protocol fees.

## Recommendation
Do not allow multiple withdraws in one buffer period.
