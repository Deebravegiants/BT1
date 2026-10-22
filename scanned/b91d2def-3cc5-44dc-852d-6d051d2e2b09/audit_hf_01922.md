# [H] The _transfer function will not work for normal users

## Summary
Severity: High
Contest weight: 0.7858
Dataset id: 10541
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _transfer function performs different checks to see if there are any constraints like
limitsInEffect, canSwap, etc. It also checks if the sender or the receiver is excluded from fees to
decide if any fees should be applied.
```solidity
if (takeFee) {
    // on sell
    if (automatedMarketMakerPairs[to] && sellFees > 0) {
        if (isAngelBuyer[from]) {
            uint256 currentFee = getCurrentAngelFee();
            fees = amount.mul(currentFee + sellFees).div(100);
        } else if (isPrivateSaleBuyer[from]) {
            uint256 currentFee = getCurrentFee();
            fees = amount.mul(currentFee + sellFees).div(100);
        } else {
            fees = amount.mul(sellFees).div(100);
        }
    }
    // on buy
    else if (automatedMarketMakerPairs[from] && buyFees > 0) {
        if (isAngelBuyer[to]) {
            uint256 currentFee = getCurrentAngelFee();
            fees = amount.mul(currentFee + buyFees).div(100);
        } else if (isPrivateSaleBuyer[to]) {
            uint256 currentFee = getCurrentFee();
            fees = amount.mul(currentFee + buyFees).div(100);
        } else {
            fees = amount.mul(buyFees).div(100);
        }
    }
}
```
The fees are designed to decrease over time and reach 0 after a specific period of time - 90 days for private
sale and 120 days for Angel sale. The getCurrentFee and getCurrentAngelFee are called to calculate
the right amount of fees.
```solidity
function getCurrentFee() public view returns (uint256) {
    uint256 daysPassed = (block.timestamp - startDate) / 60 / 60 / 24;
    uint256 currentFee = initialFee - (daysPassed * dailyDecrease);
    if (currentFee < 0) {
        currentFee = 0;
    }
    return currentFee;
}
```
The problem is that the currentFee is stored in uint256 variable which will always revert when
daysPassed * dailyDecrease > initialFee which will happen after 90 days. This is because of the
solidity compiler that will check for overflow and underflow errors and will revert. Even though there is an if
statement to set the currentFee to 0, the call will revert before that as the uint256 can never be a
negative number. The same applies to the getCurrentAngelFee where the same thing will happen but
after 120 days.

## Recommendation
Store the currentFee in int256 to allow it to be a negative number before setting it to 0.
