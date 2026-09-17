# [M] ExchangeHelper dependency can be unusable for DEX & token combination

## Summary
Severity: Medium
Reporter: Ruhum
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L624
Type: audit-issue

## Details
# ExchangeHelper dependency can be unusable for DEX & token combination

## Summary
The ExchangeHelper contract can be DOSed for a specific combination of swap contract + erc20 token. Since the Auction and Queue contracts use the ExchangeHelper they are affected by this as well.

## Vulnerability Detail
The `ExchangeHelper` contract approves `sourceTokenAmount` to the `allowanceTarget`: https://arbiscan.io/address/0xd8a0d357171bebc63cea559c4e9cd182c1bf25ef#code#F1#L31

Some tokens only allow you to approve an amount `x` if the current allowance is set to `0`. It's supposed to protect the user from the approval race condition. The most prominent token that does that is USDT.

So if somebody uses the ExchangeHelper to swap USDT and the contract doesn't use all of the approved tokens, the allowance will be `!= 0` at the end of the transaction. Subsequent swaps with the same contract and token will revert.

So the issue depends on two things:
1. the ERC20 token has to force the user to set the allowance to `0` before you can set it to any value `x`
2. the DEX or target of the ExchangeHelper call has to *not* use all of its allowance within the transaction.

To fix it, you have to set the allowance to `0` explicitly by calling the ExchangeHelper contract in a separate transaction.

## Impact
The ExchangeHelper will not be usable for a specific DEX & token combination.

## Code Snippet
```sol
        uint256 amountCredited =
            Exchange.swapWithToken(
                s.tokenIn,
                tokenOut,
                s.amountInMax + msg.value,
                s.callee,
                s.allowanceTarget,
                s.data,
                s.refundAddress
            );
```
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L624

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L237

## Tool used

Manual Review

## Recommendation
Use a custom contract that always sets the allowance to 0 at the beginning or the end of the call.
