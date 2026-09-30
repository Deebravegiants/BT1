# [H] GMXL-2 | Redemptions Incorrectly Appear Unpaused

## Summary
Severity: High
Contest weight: 0.3147
Dataset id: 20542
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function isExternalRedemptionPaused is used to determine if GM withdrawals are currently
paused, utilizing the current PnL-to-Pool Factors as one validation for a paused state.
The validation only compares against the maxPnlForAdl and maxPnlForWithdrawals with isLong =
true, although the threshold factor may be different with isLong = false. This is incorrect as the
shortPnlToPoolFactor should be compared against the MAX_PNL_FACTOR_FOR_WITHDRAWALS for
isLong = false as in MarketUtils.validateMaxPnl
Furthermore, the condition verifies that the shortPnlToPoolFactor or the longPnlToPoolFactor
should not exceed the maxPnlForWithdrawals, as GMX will revert on withdrawal execution when the
threshold is passed. However, the check also looks at the maxPnlForAdl, which does not impact
withdrawal execution on GMX.
As a result, redemptions may appear possible when the PnL-to-Pool Factor exceeds both the
maxPnlForWithdrawals and maxPnlForAdl, although that is not the case and the withdrawal will fail.
Additionally, GMX can disable withdrawal creation, execution, or a market entirely which should also
be included to verify that redemptions are paused. Because the market appears unpaused, users can
modify their collateralization when liquidations aren’t possible, or zap into more of the irredeemable
GM tokens across Dolomite.

## Recommendation
Fetch the maxPnlForWithdrawals with both isLong = true and isLong = false
For both long and short thresholds, update the validation to only check whether the
shortPnlToPoolFactor or longPnlToPoolFactor exceeds the maxPnlForWithdrawals:
bool isShortPnlTooLarge = shortPnlToPoolFactor > int256(maxPnlForWithdrawalsShort);
bool isLongPnlTooLarge = longPnlToPoolFactor > int256(maxPnlForWithdrawalsLong);
In addition, verify that the market is enabled and withdrawal features are enabled through the
Datastore.
