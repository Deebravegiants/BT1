# [H] Division by zero in CompensationPriceFinder

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23376
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CompensationPriceFinder::_zeroForOneGetFinalCompensationPrice implements two branches depending on the sign of A. The following logic executes when it is positive, but note that A will equal zero when sumX is exactly equal to rangeVirtualReserves0, i.e.:

```solidity
if (sumX >= rangeVirtualReserves0) {
    // !A! is positive, compute !D = y * (Xhat + B) + A * Yhat!, !p* = (-L + sqrt(D)) / A!.
    @> uint256 a = sumX - rangeVirtualReserves0;
    {
        (uint256 ay1, uint256 ay0) = Math512Lib.fullMul(a, sumUpToThisRange1);
        (d1, d0) = Math512Lib.checkedAdd(d1, d0, ay1, ay0);
    }
    // Compute !sqrtDX96 := sqrt(D) * 2^96 <> sqrt(D * 2^192)!
    (d1, d0) = Math512Lib.checkedMul2Pow192(d1, d0);
    // Reuse !d1, d0! to store numerator !-L + sqrt(D)!.
    (d1, d0) =
        Math512Lib.checkedSub(0, Math512Lib.sqrt512(d1, d0), 0, uint256(liquidity) << 96);
    @> (uint256 upperBits, uint256 p1) = Math512Lib.div512by256(d1, d0, a);
    assert(upperBits == 0);
    return p1.toUint160();
} else {
    // In this case, execution will revert in Math512Lib::div512by256 with DivisorZero() due to division by zero; however, the actual solution should be
    // since the quadratic term in disappears and the equation becomes linear in .
}
```

When `sumX` equals `rangeVirtualReserves0`, `A` becomes zero and the execution reverts in `Math512Lib::div512by256` with a `DivisorZero()` error due to division by zero.

## Recommendation
Handle this edge case separately.
