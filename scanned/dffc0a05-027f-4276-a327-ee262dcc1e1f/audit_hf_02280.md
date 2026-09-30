# [H] Revisited Logic in cancelUnlock()

## Summary
Severity: High
Contest weight: 0.6139
Dataset id: 12473
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The new Magpie protocol introduces a VLMGP contract as a locker for MGP. If a user locks MGP into this contract, the contract mints the same amount of vlMGP and deposits the vlMGP into MasterMagpie so that the user can get rewards. The user can unlock MGP any time, but MGP will be kept in the VLMGP contract for a cool-down period before they can be transferred to the user. In the cool-down period, the user has the chance to cancel the unlock, which re-deposits the MGP back into MasterMagpie.

To elaborate, we show below the code snippet of the cancelUnlock() routine. As the name indicates, it is used for users to cancel the unlock of the MGP in cool down. Specificaly, it invokes the _lock() routine (line 280) to deposit the MGP back into MasterMagpie. However, it comes to our attention that the _lock() function will mint the same amount of vlMGP again for the users. As a result, users vlMGP balances are doubled. As a result, users can repeat startUnlock() and unlock() to gain as many vlMGP as they want and drain all the locked MGP from the contract.
```solidity
function cancelUnlock(uint256 _slotIndex) external override whenNotPaused {
    _checkIdexInBoundary(msg.sender, _slotIndex);
    UserUnlocking storage slot = userUnlockings[msg.sender][_slotIndex];
    if (slot.endTime <= block.timestamp)
        revert NotInCoolDown();
    if (slot.amountInCoolDown == 0)
        revert UnlockedAlready();
    _lock(msg.sender, msg.sender, slot.amountInCoolDown, false);
    slot.amountInCoolDown = 0; // not in cool down anymore
    emit ReLock(msg.sender, _slotIndex, slot.amountInCoolDown);
}
```

## Recommendation
Revisit the logic of the startUnlock()/unlock() routines to avoid the double mint of vlMGP.
