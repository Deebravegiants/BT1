# [M] Improper Funding Source in Locker::_deposit_for()

## Summary
Severity: Medium
Contest weight: 0.4483
Dataset id: 12578
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _deposit_for(
    address _addr,
    uint256 _value,
    uint256 unlock_time,
    LockedBalance memory locked_balance,
    int128 vetype
) internal {
    LockedBalance memory old_locked;
    LockedBalance memory _locked = locked_balance;
    uint256 supply_before = supply;
    supply = supply_before + _value;
    old_locked.amount = _locked.amount;
    old_locked.end = _locked.end;
    // Adding existing lock, or if a lock is expired - creating a new one
    _locked.amount += uint256Toint128(_value);
    if (unlock_time != 0)
        _locked.end = unlock_time;
    locked[_addr] = _locked;
    // Possibilities:
    // Both old_locked.end could be current expired (>/< _blockTimestamp())
    // value == 0 (extend lock) or value > 0 (add to lock or extend lock)
    // _locked.end > _blockTimestamp() (always)
    _checkpoint(_addr, old_locked, _locked);
    if (_value != 0)
        require(oliveToken.transferFrom(_addr, address(this), _value), "Payment error");
    uint256 totalVeOlive = int128Touint256(user_point_history[_addr][epoch].bias);
    uint256 _epoch = epoch;
    Point memory last_point = point_history[_epoch];
    uint256 deltaVeOlive = int128Touint256(last_point.bias);
    emit Deposit(_addr, _value, _locked.end, vetype, _blockTimestamp(), totalVeOlive - deltaVeOlive);
    emit Supply(supply_before, supply_before + _value);
}
```
It comes to our attention that the _addr address is also the one to actually provide the assets, `oliveToken.transferFrom(_addr, address(this), _value)` (line 255). In fact, the msg.sender should be the one to provide the assets for locking! Otherwise, this function may be abused to lock veOLIVE tokens from users who have approved the locking contract before without their notice.

## Recommendation
Revise the above helper routine to use the right funding source to transfer the assets for locking.
