# [H] function flashLoan is vulnerable to overflow/underflow and maxFlashLoan is not used

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-10
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/33
Type: code-finding

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
function flashLoan is vulnerable to overflow/underflow when the fee is not 0. Although currently the fee is set to 0, there is a comment: "By default there is no fee, but this can be changed by overriding {flashFee}" As these contracts are upgradeable, I cannot assume that this fee will always stay 0, thus I want you to be aware of this possible issue. function flashLoan does not use SafeMath when doing the calculations and accepts an arbitrary value for the amount parameter. When the fee is above 0, it is possible to pass such a value for an amount that (amount + fee) will overflow/underflow. For example, if the fee is set to 1 and I invoke a flashLoan with an amount of max_uint, I will be minted max_uint of tokens and will need to return (burn) 0 tokens. 
Also, there is a function maxFlashLoan which returns the maximum amount of tokens available for a loan, however, this function is never used. I assume the intention was to limit the amount you can borrow but currently it has no effect.

## Recommended Mitigation Steps
Either use SafeMath here or make sure to never introduce a fee > 0. Also, make use of maxFlashLoan function.
