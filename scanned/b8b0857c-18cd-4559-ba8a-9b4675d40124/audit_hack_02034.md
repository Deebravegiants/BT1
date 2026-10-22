# [H] 6.2 Function Pool.burnRTokens Return Values

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

Function burnRTokens of Pool contract has following definition:

```
/// @return qty0 token0 quantity sent to the caller for burnt reinvestment tokens
/// @return qty1 token1 quantity sent to the caller for burnt reinvestment tokens
function burnRTokens(uint256 qty, bool isLogicalBurn)
external
returns (uint256 qty0, uint256 qty1);
```
However the qty0 and qty1 value are not assigned in the implementation of this function. Thus 0 values
will be returned instead.

The position managers rely on these return values as they implement slippage protection as follows:

```
(amount0, amount1) = pool.burnRTokens(rTokenQty, false);
require(amount0 >= params.amount0Min && amount1 >= params.amount1Min, 'Low return amounts');
```
Ultimately, the transaction will revert if amount0Min > 0 && amount1Min >0 holds.


Code corrected:

The values are now properly assigned to the return variables.
