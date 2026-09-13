# [M] 7.4 Incorrect Decimals When Handling Collateral

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The functions _closeWithdrawCollateralSkipFL and _closeWithdrawCollateral receive
multiple inputs including the ink of the relevant urn. The ink value has previously been queried from the
vat. The ink value is then used as follows:

```
require(
IERC20(exchangeData.fromTokenAddress).approve(address(exchange), ink),
"MPA / Could not approve Exchange for Token"
);
```
The ink value, however, has been adjusted to 18 decimals and hence will be incorrect here for all tokens
that do not have 18 decimals.

Note that for the functions _closeWithdrawCollateral and _closeWithdrawDai the ink value is
also incorrectly passed to wipeAndFeeGem.

Code corrected:

The updated implementation now passes cdpData.borrowCollateral instead of ink when calling
_closeWithdrawCollateralSkipFL and _closeWithdrawCollateral. Inside the called function
this parameter is called ink. Althrough this solution technically works, it is not ideal:

- Note that both functions already take the struct cdpData as parameter, so passing
    cdpData.borrowCollateral separately is redundant.
- The call to token.approve() remains unchanged. The exchange is approved to transfer the
    amount ink (which now is cdpData.borrowCollateral) however the amount the exchange will
    transfer is exchange.fromTokenAmount.

Risk accepted:

Refactoring / improvements are planned after the MVP.


An additional problem for collaterals with non 18 decimals has been uncovered in
_closeWithdrawCollateralSkipFL() after the draft report: wipeAndFreeGem() expects the
collateral amount in the unit of the collateral token and converts it to the 18 decimal representation.
However in _closeWithdrawCollateralSkipFL this conversion is already done before the second
call to wipeAndFreeGem(), hence the conversion will happen twice and result in an incorrect value for
collaterals with less than 18 decimals. This has been correct by removing the conversion before the call
to wipeAndFreeGem().
