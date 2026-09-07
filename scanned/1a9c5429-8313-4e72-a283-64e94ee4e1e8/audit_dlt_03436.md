# [M] Attacker can increase the length of `withdrawQueue` by withdrawing 0 amount of tokens frequently

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1330
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L304-L316


# Vulnerability details

## Impact

In the [AccountingManager.withdraw]() function, it doesn't check `share > 0` and it contains a few lines of statement. Thus, attacker can increase the length of `withdrawQueue` by calling this function with `share` parameter as 0 frequently which requires a little gas.
But, the keeper must consume much more gas than attacker to run the `calculateWithdrawShares` function for increased `withdrawQueue`.

## Proof of Concept

In the `AccountingManager.withdraw` function, it doesn't check `share > 0`.

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L304-L316

```solidity
File: contracts\accountingManager\AccountingManager.sol
304:     function withdraw(uint256 share, address receiver) public nonReentrant whenNotPaused {
305:         if (balanceOf(msg.sender) < share + withdrawRequestsByAddress[msg.sender]) {
306:             revert NoyaAccounting_INSUFFICIENT_FUNDS(
307:                 balanceOf(msg.sender), share, withdrawRequestsByAddress[msg.sender]
308:             );
309:         }
310:         withdrawRequestsByAddress[msg.sender] += share;
311: 
312:         // adding the withdraw request to the withdraw queue
313:         withdrawQueue.queue[withdrawQueue.last] = WithdrawRequest(msg.sender, receiver, block.timestamp, 0, share, 0);
314:         emit RecordWithdraw(withdrawQueue.last, msg.sender, receiver, share, block.timestamp);
315:         withdrawQueue.last += 1;
316:     }
```

This function contains a few lines of statement, so calling this function requires a little gas.

In the `calculateWithdrawShares` function, while looping, it calculates `TVL` function every time by calling `previewRedeem` function from L344.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1330_
