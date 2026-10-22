# [M] DODORouteProxy#externalSwap fails to return unused from tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/53
Type: sherlock-finding

## Details
0x52

medium

# DODORouteProxy#externalSwap fails to return unused from tokens

## Summary

DODORouteProxy#externalSwap takes fromTokenAmount from msg.sender but fails to send back remainder in case of exact out trades which wouldn't use the entire from token balance.

## Vulnerability Detail

    IDODOApproveProxy(_DODO_APPROVE_PROXY_).claimTokens(
        fromToken,
        msg.sender,
        address(this),
        fromTokenAmount
    );

DODORouteProxy#externalSwap transfers fromTokenAmount from msg.sender to the DODORouteProxy contract, then calls swapTarget to complete the swap. ExactOut style swaps will not use up the entire amount a majority of the time. In these cases DODORouteProxy will be left with a balance of fromToken that won't be returned to the user

## Impact

Unused fromTokenAmount will not be returned to the user

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L229

## Tool used

Manual Review

## Recommendation

In external swap allow the user to specify if trade is exactOut. In the case that it is, check the fromToken balance and return the remainder to the user
