# [M] use `safeERC20` operations in `swap` function

## Summary
Severity: Medium
Reporter: ni8mare
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L67
Type: audit-issue

## Details
# use `safeERC20` operations in `swap` function

## Summary
Use `safeTransferFrom` instead of `transferFrom` for ERC20 tokens in the`swap` function of `SwapRouter` contract. 

## Vulnerability Detail
The `transferFrom` function returns a boolean value indicating success. This parameter needs to be checked for success. Some tokens do not revert if the transfer failed but return false instead.

## Impact
Tokens that don't actually perform the transfer and return false are still counted as a correct transfer and hence token transfers could fail silently without reverting.

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/SwapRouter.vy#L67

## Tool used

Manual Review

## Recommendation
Use safeERC20 operations like OpenZeppelin recommends for Solidity. This could be useful - https://ethereum.stackexchange.com/questions/84775/is-there-a-vyper-equivalent-to-openzeppelins-safeerc20-safetransfer
