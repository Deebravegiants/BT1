# [C] 5.1.1 tradingFunctionreturns wrong invariant at bounds, allowing to steal all pool reserves

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** NormalStrategyLib.sol#L157-L

**Description:** ThetradingFunctioncomputing the invariant value ofk =Φ¹(y/K) -Φ¹(1-x) +στreturns the
wrong value at the bounds ofxandy. The bounds ofxare 0 and1e18, the bounds ofyare 0 andK, the strike
price. Ifxoryis at these bounds, the corresponding term's computation is skipped and therefore implicitly set to
0 , its initialization value.

```
int256 invariantTermX;//Φ¹(1-x)
// @audit if x is at the bounds, the term remains 0
if (self.reserveXPerWad.isBetween(lowerBoundX + 1, upperBoundX - 1)) {
invariantTermX = Gaussian.ppf(int256(WAD - self.reserveXPerWad));
}
int256 invariantTermY;//Φ¹(y/K)
// @audit if y is at the bounds, the term remains 0
if (self.reserveYPerWad.isBetween(lowerBoundY + 1, upperBoundY - 1)) {
invariantTermY = Gaussian.ppf(
int256(self.reserveYPerWad.divWadUp(self.strikePriceWad))
);
}
```
Note thatΦ¹ = Gaussian.ppfis theprobitfunction which is undefined at 0 and 1.0, but tends towards-infinity
at 0 and+infinityat1.0 = 1e18. (The closest values used in the Solidity approximation areGaussian.ppf(1)
= -8710427241990476442 ~ -8.71andGaussian.ppf(1e18-1) = 8710427241990476442 ~ 8.71.)

This fact can be abused by an attacker to steal the pool reserves. For example, they-termΦ¹(y/K)will be a
**negative value** fory/K < 0.5. Trading out allyreserve, will compute the new invariant withyset to 0 and the
y-termΦ¹(y/K) =Φ¹(0) = -infinityis set to 0 instead, increasing the overall invariant, accepting the swap.

```
// SPDX-License-Identifier: GPL-3.0-only
pragma solidity ^0.8.4;
```
```
import "solmate/utils/SafeCastLib.sol";
import "./Setup.sol";
```
```
contract TestSpearbit is Setup {
using SafeCastLib for uint256;
using AssemblyLib for uint256;
using AssemblyLib for uint128;
using FixedPointMathLib for uint256;
using FixedPointMathLib for uint128;
```
```
function test_swap_all_out()
public
defaultConfig
useActor
usePairTokens(10 ether)
allocateSome(1 ether)
{
(uint256 reserveAsset, uint256 reserveQuote) =
subject().getPoolReserves(ghost().poolId);
```
```
bool sellAsset = true;
uint128 amtIn = 2;// pass reserve-not-stale check after taking fee
uint128 amtOut = uint128(reserveQuote);
```

```
uint256 prev = ghost().quote().to_token().balanceOf(actor());
Order memory order = Order({
useMax: false,
poolId: ghost().poolId,
input: amtIn,
output: amtOut,
sellAsset: sellAsset
});
subject().swap(order);
uint256 post = ghost().quote().to_token().balanceOf(actor());
assertTrue(post > prev, "swap-failed");
}
```
```
}
```
**Recommendation:** The terms for values at the boundsΦ¹(y/K)andΦ¹(1-x)may not be set to zero as they
would mathematically correspond to+/- infinity, resulting in a wrong invariant value. Swapping out all reserves
should not be possible. As there are several other problems with one reserve value being zero, we recommend
disallowing swapping out all reserves.

```
Note that deallocating should already not allow zeroing a reserve as some initial LP tokens are locked
and the deallocated amounts are rounded down.
```
**Primitive:** Fixed commit 743829.

- Checks if either reserve is gte a respective bound. If it is, set it as close to the bound as possible, but not at
    the bound so the Gaussian.ppf function does not revert.
- If one of the reserves is set very close to its bound, the other reserve will need to be very close to its opposite
    bound, else the invariant will be very negative.
- Adds a check in adjustReserves which gets triggered during a swap to revert if either virtualX or virtualY are
    zero.
- Removes the overwritten deltaLiquidity value that would allow 0 allocates to happen in getPoolMaxLiquidity.
- Also note that I updated the 'min delta' value in the invariant tests. It looks like if either of the reserves are
    changed by >= 3 wei then the trading function is strictly monotonic. If the delta is 2 or less, there's some
    cases where the invariant does not change.

**Spearbit:** Fixed.
