# [M] Hacker can craft malicious 1inch trade to steal the dusted fund in DODORouteProxy.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/26
Type: sherlock-finding

## Details
ctf_sec

medium

# Hacker can craft malicious 1inch trade to steal the dusted fund in DODORouteProxy.sol

## Summary

Hacker can craft malicious 1inch trade to steal the fund in DODORouteProxy.sol

## Vulnerability Detail

In DODORouteProxy.sol, We have the superWithdraw function

```solidity
/// @notice used for emergency, generally there wouldn't be tokens left
function superWithdraw(address token) public onlyOwner {
    if(token != _ETH_ADDRESS_) {
        uint256 restAmount = IERC20(token).universalBalanceOf(address(this));
        IERC20(token).universalTransfer(payable(routeFeeReceiver), restAmount);
    } else {
        uint256 restAmount = address(this).balance;
        payable(routeFeeReceiver).transfer(restAmount);
    }
}
```

as the comment suggest, there may be case if the user's trade has dust balance or user send the token to the contract by mistake. 

But before the admin can step in a withdraw the fund, a hacker can step, craft malicious 1inch trade to steal the fund in DODORouteProxy.sol

The attack vector is enabled by multiple traits of the DODORouteProxy.sol:

1. the 1inch router is whitelisted.

As suggested in the comment above the DODORouteProxy.sol

> ExternalSwap is for other routers like 0x, 1inch and paraswap

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/26_
