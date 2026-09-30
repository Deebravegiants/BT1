# [M] Reliable Validation of _assertNotContract()

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 13289
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Tranchess protocol has a voting escrow contract i.e., VotingEscrow, that is used to accept community voting and measure voting powers/weights for various protocol-wide operations. In the meantime, to mitigate possible flashloan-based manipulation, the protocol is designed to ensure only whitelisted contract-based accounts as well as EOA-based accounts to create voting locks.
```solidity
function createLock(uint256 amount, uint256 unlockTime) external nonReentrant {
    _assertNotContract(msg.sender);
    unlockTime = (unlockTime / 1 weeks) * 1 weeks; // Locktime rounded down to weeks
    LockedBalance memory lockedBalance = locked[msg.sender];
    require(amount > 0, "Zero value");
    require(lockedBalance.amount == 0, "Withdraw old tokens first");
    require(unlockTime > block.timestamp, "Can only lock until time in the future");
    require(unlockTime <= block.timestamp + maxTime, "Voting lock cannot exceed max lock time");
    scheduledUnlock[unlockTime] = scheduledUnlock[unlockTime].add(amount);
    locked[msg.sender].unlockTime = unlockTime;
    locked[msg.sender].amount = amount;
    IERC20(token).transferFrom(msg.sender, address(this), amount);
    emit LockCreated(msg.sender, amount, unlockTime);
}
```
To elaborate, we show above the createLock() routine. This routine explicitly ensures the lock owner to be an EOA account (line 100). The detection logic is implemented in a helper routine _assertNotContract(). It comes to our attention that this detection logic relies on the detection of the extcodesize primitive, which returns 0 for contracts in construction, since the code is only stored at the end of the constructor execution. A more reliable approach is to validate the EOA by if (msg.sender != tx.origin).
```solidity
function _assertNotContract(address account) private view {
    if (Address.isContract(account)) {
        if (
            addressWhitelist != address(0) &&
            IAddressWhitelist(addressWhitelist).check(account)
        ) {
            return;
        }
        revert("Smart contract depositors not allowed");
    }
}
```
```solidity
function isContract(address account) internal view returns (bool) {
    // This method relies on extcodesize, which returns 0 for contracts in construction, since the code is only stored at the end of the constructor execution.
    uint256 size;
    // solhint-disable-next-line no-inline-assembly
    assembly { size := extcodesize(account) }
    return size > 0;
}
```

## Recommendation
Revise the EOA detection logic via if (msg.sender != tx.origin).
