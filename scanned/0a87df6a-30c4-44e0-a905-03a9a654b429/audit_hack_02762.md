# [M] TrueFi strategy withdrawal DoS

## Summary
Severity: Medium
Reporter: sirhashalot
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/Sherlock.sol#L469
Type: audit-issue

## Details
# TrueFi strategy withdrawal DoS

## Summary

The TrueFi strategy implements `_withdraw` differently than other Sherlock strategies. The TrueFi `withdraw` transfers USDC held by the contract to `core`, but it does not withdraw the USDC from the TrueFi protocol first. If there is insufficient USDC to transfer to the core contract, the withdrawal from Sherlock will fail, meaning users will be unable to access their tokens.

## Vulnerability Detail

The problem is in this line of code
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/Sherlock.sol#L469

This code is called by the external `redeemNFT` function, which calls `_redeemShares`, which calls `_transferTokensOut`, which calls `yieldStrategy.withdraw` in the event that `_amount > mainBalance`. If the `yieldStrategy` value is set to the TrueFi strategy and the TrueFi strategy contract holds insufficient USDC for the withdrawal (meaning the USDC held by the TrueFi strategy is less than `_amount - mainBalance` in line 469), the withdrawal will revert. The strategy owner will have to call `liquidExit` in the TrueFi strategy to withdraw value from TrueFi to make it available in the TrueFi strategy contract for withdrawals.

## Impact

The result is a user is unable to access their funds, which is a denial of service. The risk could be elevated because the issue remains until and TrueFi strategy owner finally calls `liquidExit` in the TrueFi strategy to increase the USDC supply for withdrawal, and an indefinite lack of access to funds is a bigger problem than a denial of service that involves spamming the blockchain because no added cost is needed to sustain this denial of service.

## Code Snippet

This withdrawal statement can cause a revert
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/Sherlock.sol#L469

The reason this would revert is because the `_withdraw` function for TrueFi is implemented differently and relies on the strategy holding enough USDC
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L119-L122

## Tool used

Manual Review

## Recommendation

The `_withdraw` function in the TrueFi strategy should be implemented the same way as the other strategies to prevent a denial of service and prevent users from withdrawing their funds.
