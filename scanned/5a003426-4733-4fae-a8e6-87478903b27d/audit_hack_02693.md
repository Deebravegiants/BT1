# [M] Compromised / malicious admin or governance can update maxTVL in Queue.sol to block fund deposit

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L60
Type: audit-issue

## Details
# Compromised / malicious admin or governance can update maxTVL in Queue.sol to block fund deposit

## Summary

Compromised / malicious admin or governance can update maxTVL in Queue.sol to block fund deposit

## Vulnerability Detail

there is a admin function from Queue.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L60

```solidity
    /**
     * @inheritdoc IQueue
     */
    function setMaxTVL(uint256 newMaxTVL) external onlyOwner {
        QueueStorage.Layout storage l = QueueStorage.layout();
        require(newMaxTVL > 0, "value exceeds minimum");
        emit MaxTVLSet(l.epoch, l.maxTVL, newMaxTVL, msg.sender);
        l.maxTVL = newMaxTVL;
    }
```

the function update the maxTVl internal.

the l.maxTVL is used when _deposit function is called

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

note the line

```solidity
 require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```

Given there is no lower bound limit or upper bound limit of the parameter maxTVL,

malicious or compromised governance can update the maxTVL to a very low value and block

function _deposit from being call, and then block user from depositing by calling

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L94 

```solidity
 function deposit(uint256 amount)
```

and 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L110

```solidity
     function swapAndDeposit(IExchangeHelper.SwapArgs calldata s)
```

inside Queue.sol

## consider the POC below

1. the original maxTVL is 100000 ETH. the current TVL is  800 ETH.
2. the user can deposit normally the check below pass.

```solidity
 require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```
3. an admin key is compromised and the maxTVL is set to 1 wei, or the admin accidentally set a low TVL number

4. all incoming deposit will be blocked.

## Impact

User deposit can blocked by maxTVL parameter.

## Code Snippet

## Tool used

Manual Review, hardhat

## Recommendation

We recommend Set a sanity check in setMaxTVL (adding the lower and upper bound for maxTVL) 
so governance can’t set it to unreasonable value. 

We also recommend consider using timelock for setting governance settings.
