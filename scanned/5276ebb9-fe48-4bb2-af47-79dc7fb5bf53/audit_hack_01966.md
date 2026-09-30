# [H] 6.13 Opposite Vaults Are Swapped

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function _swapVaults in LStrategy should close the position with no liquidity and open a new
one given the price move in positiveTickGrowth. The decision on which vault to close is done in the
following if condition:

```
/// @param positiveTickGrowth `true` if price tick increased
...
if (!positiveTickGrowth) {
(fromVault, toVault) = (lowerVault, upperVault);
} else {
(fromVault, toVault) = (upperVault, lowerVault);
}
```
The function closes the fromVault and creates the new vault according to the current position of
toVault. However, the code above assigns fromVault wrongly to lowerVault if the tick is


decreasing, and vice-versa if the tick is increasing. Given this error and the following requirement, the
function would fail always (as fromVault has all liquidity):

```
require(fromLiquidity == 0, ExceptionsLibrary.INVARIANT);
```
Code corrected:

The vaults were switched like:

```
if (!positiveTickGrowth) {
(fromVault, toVault) = (upperVault, lowerVault);
} else {
(fromVault, toVault) = (lowerVault, upperVault);
}
```
