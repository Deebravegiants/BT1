# [M] `_wethWithdrawTo` is vulnerable re-entrancy

## Summary
Severity: Medium
Contest weight: 0.3962
Dataset id: 743
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function `withdrawBorrowETH` invokes `_wethWithdrawTo` and later `_checkMinReserve`, however, the check of reserve is not necessary here, as function `_wethWithdrawTo` also does that after transferring the ether. However, this reserve check might be bypassed as `TransferHelper`.`_wethWithdrawTo` uses a low level call that is vulnerable to re-entrancy attacks. As this `MIN_RESERVE` sounds like an important value, you should consider preventing re-entrancy attacks here.

```solidity
// Prevents division by zero and other undesirable behavior
uint public constant MIN_RESERVE = 1000;
```

Recommend considering using [re-entrancy guard](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/security/ReentrancyGuard.sol) on all main action functions (e.g. `deposit`, `withdraw`, `borrow`,`repay`, etc…):

## Recommendation
No recommendation
