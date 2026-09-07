# [H] Partial liquidations are not possible

## Summary
Severity: High
Chain: Smart contract
Component: 2023-03-notional
Published: 2023-05-15
Source: https://github.com/sherlock-audit/2023-03-notional-judging/issues/204
Type: sherlock-finding

## Details
xiaoming90

high

# Partial liquidations are not possible

## Summary

Due to an incorrect implementation of `VaultValuation.getLiquidationFactors()`, Notional requires that a liquidator reduces an account's debt below `minBorrowSize`. This does not allow liquidators to partially liquidate a vault account into a healthy position and opens up the protocol to an edge case where an account is always ineligible for liquidation. 

## Vulnerability Detail

While `VaultValuation.getLiquidationFactors()` might allow for the resultant outstanding debt to be below the minimum borrow amount and non-zero, `deleverageAccount()` will revert due to `checkMinBorrow` being set to `true`. Therefore, the only option is for liquidators to wipe the outstanding debt entirely but users can set up their vault accounts such that that `maxLiquidatorDepositLocal` is less than each of the vault currency's outstanding debt.

https://github.com/sherlock-audit/2023-03-notional-0xleastwood/blob/main/contracts-v2/contracts/internal/vaults/VaultValuation.sol#L240-L270

```solidity
File: VaultValuation.sol
240:         int256 maxLiquidatorDepositLocal = _calculateDeleverageAmount(
241:             vaultConfig,
242:             h.vaultShareValueUnderlying,
243:             h.totalDebtOutstandingInPrimary.neg(),
244:             h.debtOutstanding[currencyIndex].neg(),
245:             minBorrowSize,
246:             exchangeRate,
247:             er.rateDecimals
248:         );
249: 
250:         // NOTE: deposit amount is always positive in this method
251:         if (depositUnderlyingInternal < maxLiquidatorDepositLocal) {
252:             // If liquidating past the debt outstanding above the min borrow, then the entire
253:             // debt outstanding must be liquidated.
254: 
255:             // (debtOutstanding - depositAmountUnderlying) is the post liquidation debt. As an
256:             // edge condition, when debt outstanding is discounted to present value, the account
257:             // may be liquidated to zero while their debt outstanding is still greater than the
258:             // min borrow size (which is normally enforced in notional terms -- i.e. non present
259:             // value). Resolving this would require additional complexity for not much gain. An
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-03-notional-judging/issues/204_
