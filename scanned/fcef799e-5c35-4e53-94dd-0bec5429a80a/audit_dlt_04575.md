# [M] No check for  `isReferralValid` if is `isReferralValid == true` or false

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/102
Type: sherlock-finding

## Details
Ch_301

medium

# No check for  `isReferralValid` if is `isReferralValid == true` or false

## Summary
`_processReferralRebate()` has no check if `isReferralValid == true`

## Vulnerability Detail
To open a trade the logic needs to invoke `_openQueuedTrade()`
We have this line of code
```solidity
 optionsContract.createFromRouter(optionParams, isReferralValid);
```
Passing `isReferralValid` to `BufferBinaryOptions.createFromRouter()` to process the referral rebate by `_processReferralRebate()`

```solidity
        uint256 referrerFee = _processReferralRebate
            optionParams.user,
            optionParams.totalFee,
            optionParams.amount,
            optionParams.referralCode,
            optionParams.isAbove,
            isReferralValid
        );  
```
The problem is when the `isReferralValid == false` the `_processReferralRebate()` will transfer  some `referrerFee` to the `referrer`

## Impact
The logic will send some fee to the `referrer`
 in case `isReferralValid == false`

## Code Snippet
```solidity
       function createFromRouter(
        OptionParams calldata optionParams,
        bool isReferralValid
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/102_
