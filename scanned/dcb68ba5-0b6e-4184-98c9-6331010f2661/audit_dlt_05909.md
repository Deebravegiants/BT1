# [?] fix: crash when typing a comma in the MM Pay custom amount input (#44521)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-07-16
Source: https://github.com/MetaMask/metamask-extension/commit/449919f4848d693a0f1c48eae9fee842d04e9764
Type: security-commit

## Details
fix: crash when typing a comma in the MM Pay custom amount input (#44521)

## **Description**

Typing a comma as the decimal separator in the MM Pay custom amount
input (Perps withdraw/deposit, mUSD conversion) crashed the extension UI
with `BigNumber Error: new BigNumber() not a number: 0,`.

The input field intentionally accepts a comma
(`/^[0-9]*[.,]?[0-9]*$/u`), but `updatePendingAmount` stored the value
without normalizing it. The comma value then reached `new
BigNumber(amountFiat)` during render, which throws, so the confirmation
crashed to the error screen on the first comma keypress.

The fix normalizes the comma to a dot inside `updatePendingAmount`, the
single point all amount input goes through before reaching state. This
matches how `snap-ui-input.tsx` and the legacy Perps withdraw page
already handle commas. Since the input regex allows at most one
separator, a single `replace(',', '.')` is enough.

## **Changelog**

CHANGELOG entry: Fixed a crash when typing a comma as the decimal
separator in the amount field of MetaMask Pay confirmations, such as
Perps withdraw or mUSD conversion

## **Related issues**

Fixes: CONF-1696

## **Manual testing steps**

1. Open an MM Pay custom amount confirmation, e.g. Perps withdraw (with
the withdraw-to-any-token flag enabled) or Perps deposit
2. Type an amount using a comma as the decimal separator, e.g. `0,5`
3. Verify the input shows `0.5`, the extension does not crash, and
quotes load for the amount
4. Verify typing with a dot (`0.5`) still works as before

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/449919f4848d693a0f1c48eae9fee842d04e9764_
