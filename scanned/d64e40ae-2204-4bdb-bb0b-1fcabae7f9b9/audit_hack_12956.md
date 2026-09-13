# [M] Deadline parameter is set to `block.timestamp` in `_direct_swap`

## Summary
Severity: Medium
Reporter: ni8mare
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L92
Type: audit-issue

## Details
# Deadline parameter is set to `block.timestamp` in `_direct_swap`

## Summary
The deadline parameter is set to `block.timestamp` in `_direct_swap`. This could lead to a bad trade for the user

## Vulnerability Detail
The `swap` function SwapRouter calls the  `_direct_swap` function which directly uses the `block.timestamp` in the `ExactInputSingleParams` struct. Protocols shouldn't set the deadline to be `block.timestamp` as a validator can hold the transaction and the block it is eventually put into will be `block.timestamp`, so this offers no protection

## Impact
This could potentially mean that the user would get a worse price than they could've gotten if their transaction was held back by the validator. More on this - https://blog.bytes032.xyz/p/why-you-should-stop-using-block-timestamp-as-deadline-in-swaps

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L92

## Tool used

Manual Review

## Recommendation
Instead of fixing the deadline to be `block.timestamp`, use a customer parameter called `_deadline` in the function with the following check:

`require(_deadline >= block.timestamp);`
