# [M] Multiple sendSALT proposals can now get approved and together all at once spend more than `5%` of the current SALT balance of the DAO

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-05
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/60
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L209


# Vulnerability details

## Summary
The [comment on L199](https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L199) above `proposeSendSALT()` clearly states (just like in the previous implementation) that:
```js
  // Only one sendSALT Ballot can be open at a time and the sending limit is 5% of the current SALT balance of the DAO.
```
The fix applied for [M-12](https://github.com/code-423n4/2024-01-salty-findings/issues/621) on [L209](https://github.com/othernet-global/salty-io/blob/main/src/dao/Proposals.sol#L209) however has changed the unique ballot name now which means multiple proposals for `proposeSendSALT()` can now be opened concurrently and drain more than `5%` of DAO's SALT balance. 

## Impact
The presence of multiple concurrent proposals for `proposeSendSALT()` means that now 2 ballots (or 20) could get approved simultaneously and all of a sudden 10% (or 100%) of DAO's SALT balance can be drained. 
In the worst case, a malicious user with large SALT balance or a group of coordinating malicious users could come together and create multiple proposals simultaneously. Since the balance of DAO does not diminish when proposal is created but only when the ballot is executed at finalization & a transfer made, 20 such proposals are enough to drain 100%. 

## Recommended Mitigation Steps
Since we want to avoid the front-running & DOS attack highlighted in M-12 while still safeguarding DAO's `95%` SALT balance, the following steps are recommended:
- Since even in the old implementation `proposeSendSALT()` could be finalized every 14 days, transferring 5% of the balance each time, similarly enforce a 14-day (or X days) of wait period between any two ballot finalizations. Let's imagine a possible scenario to make things clearer:
  - 2 proposals are created simultaneously.
  - Proposal-1 finalizes after 15 days. `5%` SALT is transferred.
  - Proposal-2 reaches quorum on the 16th day and can be finalized & passed. However, since the last sendSALT proposal made a transfer just 1 day ago, proposal-2 needs to wait another 13 days before attempting finalization again. 

- This also means the protocol will have to take care that the upper ceiling of `amount` is `5%` of the **_current balance_**. This is because when the proposal was created, the first ballot had not finalized & transferred SALT and hence `5%` would have evaluated to a greater amount. So at the time of finalization or while doing the transfer, perform a check along the lines of:
```js
  uint256 currentBalance = exchangeConfig.salt().balanceOf( address(exchangeConfig.dao()) );
  if (amount > currentBalance * 5 / 100)
    amount = currentBalance;
```



## Assessed type

Other
