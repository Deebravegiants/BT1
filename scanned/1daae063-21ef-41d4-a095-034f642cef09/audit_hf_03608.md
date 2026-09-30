# [M] `LendingTerm::debtCeiling`

## Summary
Severity: Medium
Contest weight: 0.5588
Dataset id: 19612
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `LendingTerm::debtCeiling()` function calculates the min of `creditMinterBuffer, _debtCeiling and _hardCap` as shown below:
```solidity
// return min(creditMinterBuffer, hardCap, debtCeiling)
if (creditMinterBuffer < _debtCeiling) {
    return creditMinterBuffer;
}
if (_hardCap < _debtCeiling) {
    return _hardCap;
}
return _debtCeiling;
```
However, the above minimum logic is flawed, as it does not always return the minimum of the 3 values.

## Proof of Concept
If `creditMinterBuffer` was 3, `_debtCeiling` was `5`, and `_hardCap` was 1, then the min of the 3 values should be `_hardCap` which is 1.

But instead, this condition becomes true `creditMinterBuffer < _debtCeiling`, which then returns `creditMinterBuffer`, which is incorrect.

## Recommendation
Update the `min()` logic to be correct:
```solidity
-   if (creditMinterBuffer < _debtCeiling) {
-      return creditMinterBuffer;
-   }
-   if (_hardCap < _debtCeiling) {
-      return _hardCap;
-   }
-   return _debtCeiling;
+   if (creditMinterBuffer < _debtCeiling && creditMinterBuffer < _hardCap) {
+       return creditMinterBuffer;
+   } else if (_debtCeiling < _hardCap) {
+       return _debtCeiling;
+   } else {
+       return _hardCap;
+   }
```
