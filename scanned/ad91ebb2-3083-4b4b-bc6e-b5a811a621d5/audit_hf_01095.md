# [H] Last buyer in the BondingCurve contract can experience significant fund losses if he overpays for remaining tokens

## Summary
Severity: High
Contest weight: 0.2569
Dataset id: 4199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The buy() function does not refund overpayments to the last buyer in a situation where he transfers more ETH than needed to complete the sale. This issue arises from the incorrect interaction between the solveForN() function and the following require check: require(newN <= MAX_MILLION_TOKENS * 1e18, "Max token supply reached"); The value returned by solveForN() will always be less than or equal to MAX_MILLION_TOKENS * 1e18 due to internal rounding down and the fact that the result is constrained to the maximum MAX_MILLION_TOKENS * 1e18. Therefore, the require statement using the <= comparison is always satisfied. In cases where the last buyer transfers more ETH to the buy() function than calculated by the ethForN() function, the excess funds will be lost as there is no refund mechanism to handle overpayments.

## Recommendation
Firstly, update solveForN() to return the exact MAX_MILLION_TOKENS * 1e18 value for ETH values of 10 or more. This can be achieved by adjusting the rounding in the uint256 mid calculation within the solveForN() function as follows:
uint256 mid = (low + high + 1) / 2;
Secondly, implement a refund mechanism in the buy() function for cases where solveForN() returns exactly MAX_MILLION_TOKENS * 1e18. For example:
...
uint256 newN = solveForN(newETH);
uint256 refund;
if (newN == MAX_MILLION_TOKENS * 1e18) {
refund = (netETH - (ethForN(newN) - ethForN(n)));
uint256 feeAdjustment =  refund / (100 - fees_PERCENT);
fees -=  feeAdjustment;
refund += feeAdjustment;
}
...
if (refund > 0) {
(bool refundSent, ) = address(msg.sender).call{value: refund}("");
require(refundSent, "Refund transfer failed");
}
