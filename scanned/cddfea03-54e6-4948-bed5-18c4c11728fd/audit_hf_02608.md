# [M] YieldManager.finalize can underflow for accumulatedNegativeYields

## Summary
Severity: Medium
Contest weight: 0.6964
Dataset id: 14011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The YieldManager.finalize function reduces the accumulatedNegativeYields by:
```solidity
// sharePrice = totalValue() * E27_PRECISION_BASE / (totalValue() + accumulatedNegativeYields)
// realAmount = (nominalAmount * sharePrice) / E27_PRECISION_BASE;
if (accumulatedNegativeYields > 0) {
    accumulatedNegativeYields -= (nominalAmount - realAmount);
}
```
The nominalAmount - realAmount term can underflow with nominalAmount - realAmount > accumulatedNegativeYields because of the limited share price precision and the fact that when realAmount rounds down then nominalAmount - realAmount rounds up.
This is a DoS on the withdrawal finalizations.

## Proof of Concept
```solidity
nominalAmount = 34632200351743
totalValue = nominalAmount
negYields = 1
# realAmount will be computed as
sharePrice = 34632200351743 * 1e27 / 34632200351744 = 999999999999971125138170735
realAmount = (nominalAmount * sharePrice) / E27_PRECISION_BASE = 34632200351741
nominalAmount - realAmount = 2 > 1 = negYields

And the corresponding test:
uint256 internal constant RAY = 1e27;
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

## Recommendation
One way to address this could be to simply cap accumulatedNegativeYields at 0 in case it would turn negative. The if (accumulatedNegativeYields > 0) could also better be rephrased to if (nominalAmount > realAmount) as this is the real indicator of when accumulatedNegativeYields should change.
```solidity
if (nominalAmount > realAmount) {
    accumulatedNegativeYields = _subClamped(accumulatedNegativeYields, nominalAmount - realAmount);
}

function _subClamped(uint256 x, uint256 y) internal pure returns (uint256 z) {
    unchecked {
        z = x > y ? x - y : 0;
    }
}
```
