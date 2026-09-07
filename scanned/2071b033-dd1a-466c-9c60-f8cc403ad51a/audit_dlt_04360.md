# [M] UserManager.sol#debtWriteOff may be not publicly callable after the loan is overdue by overdue blocks + maxOverdueBlocks

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/127
Type: sherlock-finding

## Details
ctf_sec

medium

# UserManager.sol#debtWriteOff may be not publicly callable after the loan is overdue by overdue blocks + maxOverdueBlocks

## Summary

debtWriteOff may be not publicly callable after the loan is overdue byoverdue blocks + maxOverdueBlocks

## Vulnerability Detail

debtWriteOff is supposed to be publicly callable after the loan is overdue byoverdue blocks + maxOverdueBlocks

```solidity
// This function is only callable by the public if the loan is overdue by
// overdue blocks + maxOverdueBlocks. This stops the system being left with
// debt that is overdue indefinitely and no ability to do anything about it.
if (block.number <= lastRepay + overdueBlocks + maxOverdueBlocks) {
    if (staker != msg.sender) revert AuthFailed();
}
```

however, this is not the case because we can calling inside the function debtWriteOff.

```solidity
  if (vouch.trust == 0) {
      cancelVouch(staker, borrower);
  }
```

Who can call cancelVouch? Only staker or borrowers.

```solidity
function cancelVouch(address staker, address borrower) public onlyMember(msg.sender) whenNotPaused {
    if (staker != msg.sender && borrower != msg.sender) revert AuthFailed();
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/127_
