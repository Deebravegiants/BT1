# [M] Incorrect data is passed to the TradingStorage.withinExposureLimit s() function. The protocol has acknowledged this issue.

## Summary
Severity: Medium
Reporter: Afriaudit, eeyore
Contest weight: 0.2198
Dataset id: 1764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When TradingStorage.withinExposureLimits() is called from the TradingCallbacks contract, the check is performed using an inaccurate OpenInterest value.
The value passed is derived from positionSizeUSDC and leverage, where positionSizeUSDC has not yet been reduced by the open fee.
If the open fee will be deducted from positionSizeUSDC, the actual OpenInterest used to update the OI storage values would be lower than the value used in the TradingStorage.withinExposureLimits() check.
This discrepancy leads to valid trades that would fit within the OI limits being rejected, resulting in potential loss of funds due to fees paid for operations such as initiating a market open trade (msg.value) and missing fees for the protocol.
TradingStorage.withinExposureLimits() uses an OpenInterest value that has not been reduced by the potential open fee, causing the rejection of valid Open market or limit orders that would otherwise fit within OI limits after fee deduction.
The incorrect behavior can be observed here and here.
Internal pre-conditions
1. The OI limits are nearly reached.
External pre-conditions
None.
Attack Path
1. A user creates a pending Open market order (not isPnl), calculating the OI limits to fit the largest possible OI trade.
2. The open fee is not correctly deducted when TradingStorage.withinExposureLimits() is used, causing the user pending market order to be rejected.
3. The user collateral is returned, but the fee is retained by the protocol, based on the assumption that an attempt was made.
• Time-sensitive function is not executed correctly.
• Loss of user funds due to fees.
• Loss of fees for protocol and referrer.

## Recommendation
For pending Open market or limit orders that are not a new isPnl orders, precalculate the open position fee and use positionSizeUSDC-fee and leverage to determine the OpenInterest passed to TradingStorage.withinExposureLimits().
