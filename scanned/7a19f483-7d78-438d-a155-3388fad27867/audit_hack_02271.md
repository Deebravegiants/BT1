# [H] `reducedFraction` does not _reduce_ in the mathematical sense

## Summary
Severity: High
Source: https://github.com/bancorprotocol/contracts-v3/blob/b2224595afab14827ee065cb65a1444d61689fb3/contracts/utility/MathEx.sol
Type: audit-issue

## Details
In the [MathEx](https://github.com/bancorprotocol/contracts-v3/blob/b2224595afab14827ee065cb65a1444d61689fb3/contracts/utility/MathEx.sol) library, the function [reducedFraction](https://github.com/bancorprotocol/contracts-v3/blob/b2224595afab14827ee065cb65a1444d61689fb3/contracts/utility/MathEx.sol#L110) does not reduce the Fraction, instead it truncates the numerator and denominator in a way that ensures it is lower than a given maximum. So, rather than using the greatest common denominator between the numerator and denominator to reduce the fraction, this `reducedFraction` function merely prunes the numerator and denominator to ensure that they are less than the provided max, and, in so doing, loses precision. In some instances the deviation between the fraction and the result of `reducedFraction` can be over 10%.

Consider either revising the function to reduce the loss of precision or renaming the function to `truncateFraction` and providing more inline documentation that makes the loss of precision clear.

**Update:** _Fixed in commit [2cb941a636dd9b0c210dd52ee90907eeb02eea6a](https://github.com/bancorprotocol/contracts-v3/commit/2cb941a636dd9b0c210dd52ee90907eeb02eea6a) and commit [56be8479ec633e0e59385dfcbe66de4759acb4bc](https://github.com/bancorprotocol/contracts-v3/commit/56be8479ec633e0e59385dfcbe66de4759acb4bc)._
