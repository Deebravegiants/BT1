# [M] Improper Funding Source In CreamyToken::_deposit_for()

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 12527
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MilkySwap has a key CreamyToken contract that provides the functionality of computing the time-dependent vote weights. By design, the vote weight decays linearly over time and the lock time cannot be more than MAXTIME (4 years). While reviewing the current locking logic, we notice the key helper routine _deposit_for() needs to be revised. To elaborate, we show below the implementation of this _deposit_for() helper routine. In fact, it is an internal function to perform deposit and lock tokens for a user. This routine has a number of arguments and the first one _addr is the address to receive the balance. It comes to our attention that the _addr address is also the one to actually provide the assets, assert ERC20(self.token).transferFrom(_addr, self, _value) (line 377). In fact, the msg.sender should be the one to provide the assets for locking! Otherwise, this function may be abused to lock tokens from users who have approved the locking contract before without their notice.
```solidity
@internal
def _deposit_for(_addr: address, _value: uint256, unlock_time: uint256, locked_balance: LockedBalance, type: int128):
    @notice Deposit and lock tokens for a user
    @param _addr User's wallet address
    @param _value Amount to deposit
    @param unlock_time New time when to unlock the tokens, or 0 if unchanged
    @param locked_balance Previous locked amount / timestamp
    _locked: LockedBalance = locked_balance
    supply_before: uint256 = self.supply
    self.supply = supply_before + _value
    old_locked: LockedBalance = _locked
    # Adding to existing lock, or if a lock is expired - creating a new one
    _locked.amount += convert(_value, int128)
    if unlock_time != 0:
        _locked.end = unlock_time
    self.locked[_addr] = _locked
    # Possibilities:
    # Both old_locked.end could be current expired (>/< block.timestamp)
    # value == 0 (extend lock) or value > 0 (add to lock or extend lock)
    # _locked.end > block.timestamp (always)
    self._checkpoint(_addr, old_locked, _locked)
    if _value != 0:
        assert ERC20(self.token).transferFrom(_addr, self, _value)
    log Deposit(_addr, _value, _locked.end, type, block.timestamp)
    log Supply(supply_before, supply_before + _value)
```

## Recommendation
Revise the above helper routine to use the right funding source to transfer the assets for locking.
