# [H] Proper CheckPoint Logic In withdraw()

## Summary
Severity: High
Contest weight: 0.6248
Dataset id: 13040
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The veSPA_v1 is a Solidity implementation of the CURVE's voting escrow. The longer users lock their SPA, the more voting power users will have. While examining the current withdrawal logic, we notice its current implementation needs to be fixed. To elaborate, we show below the related withdraw() routine. This routine is used for withdrawing the user deposit of SPA tokens.
```solidity
function withdraw() external override nonReentrant {
    address account = _msgSender();
    LockedBalance memory existingDeposit = lockedBalances[account];
    require(existingDeposit.amount > 0, "No existing lock found");
    require(existingDeposit.cooldownInitiated, "No cooldown initiated");
    require(block.timestamp >= existingDeposit.end, "Lock not expired.");
    uint128 value = existingDeposit.amount;
    LockedBalance memory oldDeposit = lockedBalances[account];
    lockedBalances[account] = LockedBalance(false, false, 0, 0);
    uint256 prevSupply = totalSPALocked;
    totalSPALocked -= value;
    // Both oldDeposit can have either expired <= timestamp or 0 end
    // existingDeposit has 0 end
    // Both can have >= 0 amount
    _checkpoint(account, oldDeposit, existingDeposit);
    IERC20Upgradeable(SPA).safeTransfer(account, value);
    emit Withdraw(account, value, block.timestamp);
    emit Supply(prevSupply, totalSPALocked);
}
```
The issue occurs when the internal function _checkpoint() is invoked. Specifically, its third argument existingDeposit (line 571) is not properly set to the correct value, i.e., the existingDeposit is intended to contain the new locked balance/end lock time for the user, which should be all 0. In other words, within the withdraw() context, all its field value shall be reset to 0 when the _checkpoint() routine is invoked.

## Recommendation
Add the following statement to reset the existingDeposit before passing it to _checkpoint() function: existingDeposit = LockedBalance(false, false, 0, 0).
