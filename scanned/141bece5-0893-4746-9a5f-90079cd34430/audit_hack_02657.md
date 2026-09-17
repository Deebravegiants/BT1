# [H] Malicious actor can forcefully send ERC20 token into the Queue.sol to perform DOS attack to block user fund deposit

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L78
Type: audit-issue

## Details
# Malicious actor can forcefully send ERC20 token into the Queue.sol to perform DOS attack to block user fund deposit

## Summary

Malicious actor can forcefully send ERC20 token into the Queue.sol to block user fund deposit

## Vulnerability Detail

the _deposit function in QueueInternal.sol is implemented below

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L78

```solidity
  function _deposit(QueueStorage.Layout storage l, uint256 amount) internal {
        require(amount > 0, "value exceeds minimum");

        // the maximum total value locked is the sum of collateral assets held in
        // the queue and the vault. if a deposit exceeds the max TVL, the transaction
        // should revert.
        uint256 totalWithDepositedAmount =
            Vault.totalAssets() + ERC20.balanceOf(address(this));
        require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```

the two line of code below open a attack vector for malicious actor.

```solidity
uint256 totalWithDepositedAmount =
            Vault.totalAssets() + ERC20.balanceOf(address(this));
require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```

Because ERC20 balanceOf is used. Malicious actor can forcefully send ERC20 token into the Queue.sol to block user fund deposit by increasing the contract balance.

Then total deposited plus balance would exceed maxTVL, and no fund can be deposited until maxTVL is manually adjusted

then block user from depositing by calling

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L94 

```solidity
 function deposit(uint256 amount)
```

and 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L110

```solidity
     function swapAndDeposit(IExchangeHelper.SwapArgs calldata s)
```

## Consider this POC

1. the maxTVL is 100 ETH. the totalWithDepositedAmount is 98 ETH.
2. The user wants to deposit 1 ETH, 98 ETH  plus1 ETH is smaller than 100 ETH, so user should be able to deposit fund.
3. At this time, a malicious actor forcefully send 3 ETH to the Queue.sol contract
4. now ERC20 balanceOf is 3 ETH. 
5. User is not able to deposit fund because according to the logic

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L84

```solidity
uint256 totalWithDepositedAmount =
            Vault.totalAssets() + ERC20.balanceOf(address(this));
require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```

-----

```solidity
totalWithDepositedAmount + ERC20 balance > max TVL, where 

totalWithDepositedAmount = 98 ETH
ERC20 balance is 3 ETH
new TVL is 100
```

## Impact

User cannot deposit fund

## Code Snippet

## Tool used

Manual Review, hardhat

## Recommendation

We recommend the project get rid of using ERC20 BalanceOf
