# [H] DODOApprove.sol : "function init" can be called anyone and takeover the ownership

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/74
Type: sherlock-finding

## Details
ak1

high

# DODOApprove.sol : "function init" can be called anyone and takeover the ownership

## Summary
In DODOApprove.sol, the function "init" is used to set the `owner` and `initProxyAddress`.
Since it is declared as external and there are no access restriction modifier like `onlyowner`, anyone can call the function and take ownership of this contract.

## Vulnerability Detail

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L45-L48

    function init(address owner, address initProxyAddress) external {
        initOwner(owner);
        _DODO_PROXY_ = initProxyAddress;
    }

as init function is external, ownership can be taken by anyone.

## Impact
Malicious actor can take the control of this contract and change any value that depends on the owner.
Below line of codes shows the function that could be handled by the owner.
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L50-L69

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L45-L48

## Tool used

Manual Review

## Recommendation
Use onlyowner modifier so that existing owner only can call this function.

    function init(address owner, address initProxyAddress) external onlyOwner  {

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/74_
