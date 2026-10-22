# [H] updatePositionFromBalanceMargin function re-

## Summary
Severity: High
Contest weight: 0.7877
Dataset id: 22891
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a cross position is closed all the other cross positions "fromBalance"s updated. If the amount to be updated is negative then the other positions "fromBalance" should be decreased to lower down their cross available value. However, the function logic always returns "0" prior to storage update before the return statement.

Say Bob has 3 positions as follows:  
WBTC SHORT (margin: 100, marginFromBalance: 100, initialMarginInUsd: 100, initialMarginInUsdFromBalance: 100)  
SOL SHORT (margin: 100, marginFromBalance: 50, initialMarginInUsd: 100, initialMarginInUsdFromBalance: 50)  
WETH SHORT (margin: 100, marginFromBalance: 90, initialMarginInUsd: 100, initialMarginInUsdFromBalance: 90)

Say the WBTC position is closed in loss such that there is a negative settledMargin. The changeToken will also be negative. Say the value for changeToken is -110.

Below lines will be executed in PositionMarginProcess::updatePositionFromBalanceMargin() function since the changeToken is negative. For SOL the addBorrowMarginInUsd will be 110 * 100 / 100 = 110. Since this value is higher than position.initialMarginInUsdFromBalance the first if check will be executed and position.initialMarginInUsdFromBalance will be "0". Then, the actual changeAmount will be calculated right after, normally this value should be the 50 * 100 / 100 = 50 token. However, because the "position" is a storage pointer and its value is set to "0" before the changeAmount calculation, changeAmount calculation will also be "0". That means that when the loop goes to the WETH position, instead of only decreasing 60 tokens (110 - 50) it will also reset the entire position.initialMarginInUsdFromBalance for the WETH position.

```solidity
else {
    uint256 addBorrowMarginInUsd = (-amount).toUint256().mul(position.initialMarginInUsd).div(position.initialMargin);
    if (position.initialMarginInUsdFromBalance <= addBorrowMarginInUsd) {
        position.initialMarginInUsdFromBalance = 0;
        changeAmount = position.initialMarginInUsdFromBalance.mul(position.initialMargin).div(position.initialMarginInUsd);
    } else {
        position.initialMarginInUsdFromBalance -= addBorrowMarginInUsd;
        changeAmount = (-amount).toUint256();
    }
}
```

Entire "from balance" will be off. Account will have a lower "from balance" which means that the account can borrow more although it shouldn't be. No coded poc here because the issue is clear from text and easy to spot.

## Recommendation
Change the order of these lines to this:
```solidity
changeAmount = position.initialMarginInUsdFromBalance.mul(position.initialMargin).div(position.initialMarginInUsd);
position.initialMarginInUsdFromBalance = 0;
```
