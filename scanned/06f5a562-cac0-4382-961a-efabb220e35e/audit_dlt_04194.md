# [H] DODOApproveProxy.sol : "function init" can be called by anyone and can take the ownership

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/75
Type: sherlock-finding

## Details
ak1

high

# DODOApproveProxy.sol : "function init" can be called by anyone and can take the ownership

## Summary
In `DODOApproveProxy.sol`, the function `init` is used to set the owner and allow the proxy address for setting `_IS_ALLOWED_PROXY_[proxies[i]] = true;.` Since this function is declared as external, anyone can call this and take ownership.

## Vulnerability Detail

    function init(address owner, address[] memory proxies) external {
        initOwner(owner);
        for(uint i = 0; i < proxies.length; i++) 
            _IS_ALLOWED_PROXY_[proxies[i]] = true;
    }

The `init` function is declared as external, anyone can call and take the ownership.

## Impact
The malicious user can influence all the owner dependent functions.

The functions that are controlled by owner are,

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApproveProxy.sol#L53-L71

This can cause issue in multiple ways. even the contract can be completely blocked or self destructed.
The user can unilaterally change any of the core functionality. 
They can implement their custom token contract and use it to siphon the funds from dodo.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApproveProxy.sol#L47-L51

## Tool used

Manual Review


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/75_
