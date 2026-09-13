# [M] 5.3.1 Point.positionis not updated forstackslots in_removeStackPosition.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:**

- LienToken.sol#L402
- LienToken.sol#L809
**Description:** In _createLien, when a new stack slot is created, thenewSlot.point.position is set to
uint8(params.stack.length)which would be its index in thestack.
When _removeStackPosition is called to remove a slot from the stack at index position, the
newStack[i].point.positionis not updated for indexes that are greater thanpositionin the originalstack.
Alsoslot.point.positionis only used when we emitAddLienandLienStackUpdatedevents. In both of those
cases, we could have usedparams.stack.length
**Recommendation:** If it is necessary to keepslot.point.positiondue to future upgrades, make sure to update
_removeStackPositionso that it updates the positions as well.
Otherwise,slot.point.positioncan be removed.
**Astaria:** Issue is fixed in commit fa175c by removing theslot.point.position.
**Spearbit:** Verified.
