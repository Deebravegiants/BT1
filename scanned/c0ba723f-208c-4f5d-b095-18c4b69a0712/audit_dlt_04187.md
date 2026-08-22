# [M] `superWithdraw` function cannot withdraw any normal ERC-20 tokens, which doesnt implement `universal` functions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/89
Type: sherlock-finding

## Details
ElKu

medium

# `superWithdraw` function cannot withdraw any normal ERC-20 tokens, which doesnt implement `universal` functions

## Summary

[superWithdraw](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L146) in `DODORouteProxy` contract is intended for withdrawing any tokens which are stuck in the contract. This method assumes that the functions stuck are `UniversalERC20` tokens which have implemented methods like `universalBalanceOf` and `universalTransfer`. If any normal ERC-20 tokens are stuck in the contract, they wont be able to be withdrawn.

## Vulnerability Detail

Looking at the `superWithdraw` implementation:

```solidity
    function superWithdraw(address token) public onlyOwner {
        if(token != _ETH_ADDRESS_) {
            uint256 restAmount = IERC20(token).universalBalanceOf(address(this));  //@audit cant withdraw normal ERC20.
            IERC20(token).universalTransfer(payable(routeFeeReceiver), restAmount);
        } else {
            uint256 restAmount = address(this).balance;
            payable(routeFeeReceiver).transfer(restAmount);  //@audit use call instead of transfer
        }
    }
```

when the token is not equal to eth address, the amount of token stuck in the contract is calculated by calling the `universalBalanceOf` method. But this method is not available in normal ERC-20 tokens. Which means the function will revert and we will never be able to withdraw those tokens.

## Impact

Tokens which doesnt implement [UniversalERC20](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol) methods, if accidentally sent to the contract are forever stuck and lost.

## Code Snippet

```solidity
    function superWithdraw(address token) public onlyOwner {
        if(token != _ETH_ADDRESS_) {
            uint256 restAmount = IERC20(token).universalBalanceOf(address(this));  //@audit cant withdraw normal ERC20.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/89_
