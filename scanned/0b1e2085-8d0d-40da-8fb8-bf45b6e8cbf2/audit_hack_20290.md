# [M] 5.3.15potentialDebtis not compared against a new lien'smaxPotentialDebtin_appendStack.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LienToken.sol#L435-L439
**Description:** In_appendStack, we have the following block:

```
newStack = new Stack[](stack.length + 1);
newStack[stack.length] = newSlot;
uint256 potentialDebt = _getOwed(newSlot, newSlot.point.end);
...
if (
stack.length > 0 && potentialDebt > newSlot.lien.details.maxPotentialDebt
) {
revert InvalidState(InvalidStates.DEBT_LIMIT);
}
```
Note, we are only performing a comparison betweennewSlot.lien.details.maxPotentialDebtandpoten-
tialDebtwhenstack.length > 0. If_createLienis called withparams.stack.length == 0, we would not
perform this check and thus the inputparamsis not fully checked for misconfiguration.
**Recommendation:** Make sure to perform this check in either_createLienor here in_appendStackby removing
thestack.length > 0condition:
//`potentialDebt`needs to be calculated in`_createLien`
if ( potentialDebt > params.lien.details.maxPotentialDebt ) {
revert InvalidState(InvalidStates.DEBT_LIMIT);
}

**Astaria:** Acknowledged.
**Spearbit:** Acknowledged.
