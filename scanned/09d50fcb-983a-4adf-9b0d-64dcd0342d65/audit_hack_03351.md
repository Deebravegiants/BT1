# [M] All tokens and eth that is accidentally sent to DODORouteProxy can be stealed by user

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L182
Type: audit-issue

## Details
# All tokens and eth that is accidentally sent to DODORouteProxy can be stealed by user

## Summary
All tokens and eth that is accidentally sent to DODORouteProxy can be stealed by user because amount of tokens that is provided to the `externalSwap` function and amount provided `callDataConcat` can be different. 
## Vulnerability Detail
Function DODORouteProxy.externalSwap takes `fromTokenAmount` param which means how many tokens user wants to swap. 
But it doesn't check that the amount provided inside `callDataConcat` param is the same.
This allows for user to provide bigger amount of tokens inside `callDataConcat` param. And because of [maximum allowance](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L182) for the swap contract the call will be successful if DODORouteProxy has this amount of tokens.

Despite that DODORouteProxy is not going to hold funds, however they can be sent there accidentally or not.
For such reason DODORouteProxy even has function `superWithdraw` that allows to send those tokens to the fee recipient.

So in case when DODORouteProxy controls some token, attacker can make a swap from that token to another token and provide more amount inside `callDataConcat` to sweep all tokens.

For the eth it's even simplier, attacker just need to call swap and provide `fromTokenAmount == DODORouteProxy.balance`.
## Impact
DODORouteProxy funds are swept.
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
In ETH swaps do not send more than `msg.value`. For tokens swaps do not provide max allowance for the external protocols, provide allowance for swap amount only.
