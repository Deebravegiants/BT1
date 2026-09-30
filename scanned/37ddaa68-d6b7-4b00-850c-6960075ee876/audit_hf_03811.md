# [M] MarketUtils.getFundingAmountPerSizeDelta()

## Summary
Severity: Medium
Contest weight: 0.6008
Dataset id: 20030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MarketUtils.getFundingAmountPerSizeDelta() has a rounding logical error. The main problem is the divisor always use a roundupDivision regardless of the input roundUp rounding mode. Actually the correct use should be: the divisor should use the opposite of roundUp to achieve the same logic of rounding. MarketUtils.getFundingAmountPerSizeDelta() is used to calculate the FundingAmountPerSizeDelta with a roundUp input mode parameter.  
gmx-synthetics/contracts/market/MarketUtils.sol#L1126-L1136  
This function is used for example by the IncreaseLimit order via flow OrderHandler.executeOrder() -> _executeOrder() -> OrderUtils.executeOrder() -> processOrder() -> IncreaseOrderUtils.processOrder() -> IncreasePositionUtils.increasePosition() -> PositionUtils.updateFundingAndBorrowingState() -> MarketUtils.updateFundingAmountPerSize() -> getFundingAmountPerSizeDelta(). However, the main problem is the divisor always use a roundupDivision regardless of the input roundUp rounding mode. Actually the correct use should be: the divisor should use the opposite of roundUp to achieve the same logic of rounding. My POC code confirms my finding: given fundingAmount = 2e15, openInterest = 1e15+1, and roundUp = true, the correct answer should be: 1999999999999998000000000000001999999999999999. However, the implementation returns the wrong solution of: 1000000000000000000000000000000000000000000000. The reason is that actually rounded down rather than rounding up!
```solidity
function testGetFundingAmountPerSizeDelta() public{
    uint result = MarketUtils.getFundingAmountPerSizeDelta(2e15, 1e15+1, true);
    console2.log("result: %d", result);
    uint256 correctResult = 2e15 * 1e15 * 1e30 + 1e15; // this is a real round up
    correctResult = correctResult/(1e15+1);
    console2.log("correctResult: %d", correctResult);
    assertTrue(result == 1e15 * 1e30);
}
```
MarketUtils.getFundingAmountPerSizeDelta() has a rounding logical error, sometimes, when roundUp = true, the result, instead of rounding up, it becomes a rounding down!

## Recommendation
Change the rounding mode of the divisor to the opposite of the input roundUp mode. Or, the solution can be just as follows:
```solidity
function getFundingAmountPerSizeDelta(
    uint256 fundingAmount,
    uint256 openInterest,
    bool roundUp
) internal pure returns (uint256) {
    if (fundingAmount == 0 || openInterest == 0) { return 0; }
    // how many units in openInterest
    // uint256 divisor = Calc.roundUpDivision(openInterest, Precision.FLOAT_PRECISION_SQRT);
    // return Precision.toFactor(fundingAmount, divisor, roundUp);
    return Precision.toFactor(fundingAmount * Precision.FLOAT_PRECISION_SQRT, openInterest, roundUp);
}
```
