# [M] Improper Funding Source In VotingEscrow::_deposit_for()

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 13364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The VRH DAO has a key VotingEscrow contract that provides the functionality of computing the time-dependent vote weights. By design, the vote weight decays linearly over time and the lock time cannot be more than MAXTIME (4 years). While reviewing the current locking logic, we notice the key helper routine _deposit_for() needs to be revised. To elaborate, we show below the implementation of this _deposit_for() helper routine. In fact, it is an internal function to perform deposit and lock tokens for a user. This routine has a number of arguments and the first one _addr is the address to receive the balance. The second _from address is the account that actually provides the assets, assert ERC20(self.token).transferFrom(_from, self, _value) (line 366). However, it comes to our attention that is caller deposit_for() uses the same given addr as the first argument and the second argument! As a result, the current implementation may be abused to lock tokens from users who have approved the locking contract before without their notice. To fix, there is a need to use the msg.sender as the second argument to provide the assets for locking!
```solidity
@external
@nonreentrant(lock)
def deposit_for(_addr: address, _value: uint256):
    @notice Deposit _value tokens for _addr and add to the lock
    @dev Anyone (even a smart contract) can deposit for someone else, but cannot extend their locktime and deposit for a brand new user
    @param _addr User's wallet address
    @param _value Amount to add to user's lock
    _locked: LockedBalance = self.locked[_addr]
    assert _value > 0  # dev: need non-zero value
    assert _locked.amount > 0, "No existing lock found"
    assert _locked.end > block.timestamp, "Cannot add to expired lock. Withdraw"
    self._deposit_for(_addr, _addr, _value, 0, self.locked[_addr], DEPOSIT_FOR_TYPE)

@internal
def _deposit_for(_addr: address, _from: address, _value: uint256, unlock_time: uint256, locked_balance: LockedBalance, type: int128):
    @notice Deposit and lock tokens for a user
    @param _addr User's wallet address
    @param _value Amount to deposit
    @param unlock_time New time when to unlock the tokens, or 0 if unchanged
    @param locked_balance Previous locked amount/timestamp
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
        assert ERC20(self.token).transferFrom(_from, self, _value)
    log Deposit(_from, _addr, _value, _locked.end, type, block.timestamp)
    log Supply(supply_before, supply_before + _value)
```

## Recommendation
Revise the above calling routine to use the right funding source to transfer the assets for locking.
