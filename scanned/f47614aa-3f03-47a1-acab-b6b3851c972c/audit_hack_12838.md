# [M] USDT: set allowance to be 0 first

## Summary
Severity: Medium
Reporter: ni8mare
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L68C1-L68C1
Type: audit-issue

## Details
# USDT: set allowance to be 0 first

## Summary
To approve tokens like USDT, set their allowance to 0 first and then approve with the intended amount.

## Vulnerability Detail
Some tokens like USDT require that the allowance should be set to 0 first and then be set to the new value. This means if you’re only using `approve `and not resetting the `allowance`, you won’t be able to allow a different amount until the `allowance` is reset first.

## Impact
It won't be possible to use ERC20 tokens like USDT.

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L68C1-L68C1

## Tool used

Manual Review

## Recommendation
Approve to 0 first, then approve the intended amount.
