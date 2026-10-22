# [M] Pairs with "MAX_FEE" can revert due to round-

## Summary
Severity: Medium
Contest weight: 0.4536
Dataset id: 22446
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
If the pair has set the max fee by the fee controller admin which is "1_000" then depending on the amount to be swapped, the tx can revert due to rounding error.
When the fee amount is calculated inside the RubiconFeeController, the fee amount is rounded down.
uint256 feeAmount = fee.applyFee
? order.outputs[i].amount.mulDivUp(fee.fee, DENOM)
: order.outputs[i].amount.mulDivUp(baseFee, DENOM);
then, ProtocolFees abstract contract will do a double check on the fee taken as follows:
if (feeOutput.amount > tokenValue.mulDivDown(MAX_FEE, DENOM)) {
revert FeeTooLarge(
feeOutput.token,
feeOutput.amount,
feeOutput.recipient
);
}
As we can see, it uses mulDivDown, so if the calculation in the FeeController rounds up, the transaction will revert.
Textual PoC: Suppose the fee pair is set to "1_000" for tokens A and B. Alice sends an order to sell "111111111111111111111" (111.11 in 18 decimals) token A for token B.
Within the fee controller, the fee amount will be calculated as: 111111111111111111111 * 1000 / 100_000 (roundUp) = 1111111111111111112
Subsequently, during execution, within the ProtocolFees contract, the maximum fee amount will be computed as: 111111111111111111111 * 1000 / 100_000 (roundDown) = 1111111111111111111
Consequently, the transaction will revert because 1111111111111111111 > 
Coded PoC:
// forge test --match-contract GladiusReactorTest --match-test test_FeesRounding -vv
function test_FeesRounding(uint amount) external {
// @dev there will be plenty of values reverting this test.
vm.assume(amount <= type(uint128).max);
vm.assume(amount >= 1e6);
uint DENOM = 100_000;
uint FEE = 1_000;
assertEq(resultDown, resultUp);
}
above, the resulting output shouldn't overflow MAX_FEE, but other possibilities of reverts are known/acceptable. Any fee setting in range 0<MAX_FEE should not revert and if it reverts then its acceptable. Hence, I'll label this as medium.
```

## Recommendation
No recommendation available
