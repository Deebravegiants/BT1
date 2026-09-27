# [M] Withdrawal with zero amount is possible

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

When creating a withdrawal request, the amount of tokens to withdraw is passed as a parameter: 


**code/contracts/PolicyBook.sol:L358**
```solidity
function requestWithdrawal(uint256 _tokensToWithdraw) external override {
```

The problem is that this parameter can be zero, and the function will be successfully executed. Moreover, this request can then be added to the queue, and the actual withdrawal will also be executed with zero value. Addresses that never added any liquidity could spam the system with these requests.

#### Recommendation

Do not allow withdrawals of zero tokens.
