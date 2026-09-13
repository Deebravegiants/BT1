# [M] Invalidating the withdraw request NFT will make the eEth stuck in the contract

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-11
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/49
Type: hats-finding

## Details
**Github username:** @Krishnakumarskr
**Submission hash (on-chain):** 0x4cbf51810f2752e2e38b218c5f55d8c70622c5d72fb73a39244d2910b3681617
**Severity:** medium

**Description:**
**Description**

This issue has two sub-issues.

*For both issues we have a common assumption:*

Assuming that the `_report.finalizedWithdrawalAmount` [link](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiAdmin.sol#L195) doesn’t include the amount for invalid requests from `EtherFiNodeAdmin.sol::_handleWithdrawals()`.

\
Issue 1: **eEth transferred to withdrawRequest might stuck if it's in an invalid state or can only be claimed by an invalid requester.**


Though `WithdrawRequestNFT::invalidateRequest()` does not allow the requester to claim the withdrawal amount, the only way to burn the eETH out of this request is to make the request valid again.

But making it valid will allow the invalid requester to make a claim where the actor can withdraw the ETH from the liquidity pool. If it's in an invalid state then the eEth will be stuck in the contract forever. There is no other way to take the eEth out or burn it.


Issue 2: **A valid request may not be able to claim withdrawal**

Making a request valid again from the invalid state `WithdrawRequestNFT::validateRequest()` should also increment the `LiquidityPool::ethAmountLockedForWithdrawal`. Otherwise, at some point, a valid request cannot withdraw the amount because of the condition `ethAmountLockedForWithdrawal < _amount` in `LiquidityPool::withdraw()` [link](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L178).


\
If our assumption is false, means if the `_report.finalizedWithdrawalAmount` includes the amount for the invalid request also, then `invalidateRequest()` should decrement the `ethAmountLockedForWithdrawal` otherwise at some point the condition `ethAmountLockedForWithdrawal < _amount` will result true most of the time, since the locked amount includes for both valid and invalid state.

**Mitigation**

- The solution for Issue 1 is to introduce a function that allows the protocol to claim the withdrawal if the request is invalid and burn the eEth.
- The solution for Issue 2 is to add and send both valid and invalid withdrawal request amount in the report to the handleWithdrawals method and add it to `ethAmountLockedForWithdrawal`.
    
   Then, call a function in invalidateRequest and validateRequest to decrement and increment the `ethAmountLockedForWithdrawal` respectively.
