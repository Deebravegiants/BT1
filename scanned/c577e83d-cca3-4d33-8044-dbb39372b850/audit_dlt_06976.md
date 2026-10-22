# [M] Incorrect withdrawal requested

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-yieldy
Published: 2022-06-25
Source: https://github.com/code-423n4/2022-06-yieldy-findings/issues/56
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-yieldy/blob/main/src/contracts/Staking.sol#L319


# Vulnerability details

## Impact
_requestWithdrawalFromTokemak function :: Instead of sending amountToRequest for requestWithdrawal, contract is asking _amount for requestWithdrawal. This becomes a problem when balance < _amount and only balance could be withdrawn

## Proof of Concept
1. In _requestWithdrawalFromTokemak function, amountToRequest is calculated as

```
// the only way balance < _amount is when using unstakeAllFromTokemak
        uint256 amountToRequest = balance < _amount ? balance : _amount;
```

2. Now assuming balance < _amount then amountToRequest becomes balance

3. But tokePoolContract.requestWithdrawal is called over _amount instead of amountToRequest which means withdrawal is requested over an extra amount

## Recommended Mitigation Steps
Modify Staking.sol#L326 to

```
if (amountToRequest > 0) tokePoolContract.requestWithdrawal(amountToRequest);
```
