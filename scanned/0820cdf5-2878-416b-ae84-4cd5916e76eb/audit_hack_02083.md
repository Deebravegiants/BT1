# [M] 7.3 Impossible Decrease Operations

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

wipeAndFreeGem() is used in each decrease operation to withdraw collateral from the vault to the
MultiplyProxyActions contract. However, the function reverts if the collateral has less than 18 decimals.

```
function wipeAndFreeGem(
address manager,
address gemJoin,
uint256 cdp,
uint256 borrowedDai,
uint256 collateralDraw
) public {
...
uint256 wadC = convertTo18(gemJoin, collateralDraw);
IManager(manager).frob(cdp, -int256(wadC), _getWipeDart(vat, IVat(vat).dai(urn), urn, ilk));
IManager(manager).flux(cdp, address(this), wadC);
IJoin(gemJoin).exit(address(this), wadC);
}
```

Following scenario could occur if the collateral is GUSD which has only two decimals.

```
1.Parameter collateralDraw is converted to 18 decimals representations which is stored in local
variable wadC. Meaning that wadC == collateralDraw * (10**16).
2.frob and flux are called with wadC as part of the argument.
3.GemJoin.exit() is also called with wadC as an argument.
```
```
4.In GemJoin contract's exit(), the GemJoin contract will try to call the GUSD contract to transfer
wadC tokens.
5.The transaction reverts since wadC is much higher than the balance in GUSD of GemJoin at that
moment.
```
Since exiting creates a transfer in the GUSD contract, it must use the amount of decimals the token has.

Code corrected:

collateralDraw instead of wadC is now passed to the call to gemJoin.exit() which is in the correct
unit.
