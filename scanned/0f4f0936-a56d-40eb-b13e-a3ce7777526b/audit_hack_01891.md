# [H] 6.1 Overflow Might DOS the App

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

The _tradeTargetAmount and _tradeSourceAmount functions compute the input/output needed to
perform a trade in a Strategy. However, Strategy inputs are only constrained by the z variable which
should be greater or equal to y. This implies that A or B can be set arbitrarily by a user and z has no no
limit to the upside.

Let's take the example of _tradeTargetAmount:

```
function _tradeTargetAmount(uint256 x, Order memory order) private pure returns (uint128) {
uint256 y = uint256(order.y);
uint256 z = uint256(order.z);
uint256 A = uint256(order.A);
uint256 B = uint256(order.B);
```
```
if (A == 0) {
return MathEx.mulDivF(x, B * B, ONE * ONE).toUint128();
}
```
```
uint256 temp1 = y * A + z * B;
uint256 temp2 = (temp1 * x) / ONE;
uint256 temp3 = temp2 * A + z * z * ONE;
return MathEx.mulDivF(temp1, temp2, temp3).toUint128();
}
```
Here, z could potentially be type(uint128).max, which would imply that the temp3 computation
overflows, and the transaction reverts.

An attacker could create a simple Strategy with all parameter values (except the liquidity) maxed out.
This Strategy will yield great results in the SDK: It returns extremely favorable rates for any trade. And as
the computation in the SDK is not bound by 256 bit limits, these rates will always be sorted to the top of


each getTradeData call without errors. This results in all users relying on the SDK now trading against
a Strategy that reverts on-chain.

Note that it might also happen when the mulDiv function's result ends up greater than
type(uint128).max due to the safe downcast to 128 bits.

Code corrected:

The SDK now incorporates checks to verify that each calculation (e.g., mulDivC) does not exceed 256
bits and does not go below 0. Additionally, the functions _tradeSourceAmount and
_tradeTargetAmount now calculate factors that are used to scale down intermediate numbers that are
too big to fit in 256 bits.
