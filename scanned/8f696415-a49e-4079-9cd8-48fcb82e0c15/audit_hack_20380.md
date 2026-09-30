# [M] 5.3.1 YieldManager.finalizecan underflow foraccumulatedNegativeYields.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** YieldManager.sol#L

**Description:** TheYieldManager.finalizefunction reduces theaccumulatedNegativeYieldsby:

```
// sharePrice = totalValue() * E27_PRECISION_BASE / (totalValue() + accumulatedNegativeYields)
// realAmount = (nominalAmount * sharePrice) / E27_PRECISION_BASE;
if (accumulatedNegativeYields > 0) {
accumulatedNegativeYields -= (nominalAmount - realAmount);
}
```
ThenominalAmount - realAmountterm can underflow withnominalAmount - realAmount > accumulatedNeg-
ativeYieldsbecause of the limited share price precision and the fact that whenrealAmountrounds down then
nominalAmount - realAmountrounds up.

This is a DoS on the withdrawal finalizations.

**Recommendation:** One way to address this could be to simply capaccumulatedNegativeYieldsat 0 in case it
would turn negative. Theif (accumulatedNegativeYields > 0)could also better be rephrased toif (nomi-
nalAmount > realAmount)as this is the real indicator of whenaccumulatedNegativeYieldsshould change.

```
if (nominalAmount > realAmount) {
accumulatedNegativeYields = _subClamped(accumulatedNegativeYields, nominalAmount - realAmount);
}
```
```
function _subClamped(uint256 x, uint256 y) internal pure returns (uint256 z) {
unchecked {
z = x > y? x - y : 0;
}
}
```
**Proof of Concept** :

```
nominalAmount = 34632200351743
totalValue = nominalAmount
negYields = 1
```
```
# realAmount will be computed as
sharePrice = 34632200351743 * 1e27 / 34632200351744 = 999999999999971125138170735
realAmount = (nominalAmount * sharePrice) / E27_PRECISION_BASE = 34632200351741
nominalAmount - realAmount = 2 > 1 = negYields
```
And the corresponding test:

```
uint256 internal constant RAY = 1e27;
```
```
function test_math(uint120 _nominalAmount, uint120 _totalValue, uint120 _negYields) public {
vm.assume(_negYields > 0);
uint256 negYields = _negYields;
uint256 totalValue = _totalValue;
uint256 nominalAmount = bound(_nominalAmount, 0, totalValue);
uint256 sharePrice = totalValue * RAY / (totalValue + negYields);
uint256 realAmount = nominalAmount * sharePrice / RAY;
// uint256 realAmount = (nominalAmount * totalValue) / (totalValue + negYields);
assertGe(negYields, nominalAmount - realAmount);
}
```

# DRAFT
