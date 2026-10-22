# [H] H-04 | Unhandled ADL Case Can Lead To Stuck Funds

## Summary
Severity: High
Contest weight: 0.3091
Dataset id: 21944
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GmxUtils contract doesn’t account for Automatic Deleveraging (ADL) from GMX, which can
partially or fully close proﬁtable positions if pending proﬁts exceed the market's threshold.
During an ADL event, the receiver variable is set to the account address, which in this case is the
GmxUtils contract. Since the GmxUtils contract doesn’t set a savedCallbackContract (which is used
as the callback contract for ADLs), the callback address will default to the zero address.
As a result, the ADL callback will not be triggered, meaning the ADL event won't be properly handled.
This causes any funds sent to the GmxUtils contract to become stuck with no way to retrieve them.
Additionally, these funds will no longer be included in share calculations, leading to discrepancies in
share distribution and vault accounting, as they aren’t in the PerpetualVault contract or the GMX
position.
If the position is closed, further calls to GMX, such as withdrawal requests, could lead to a denial of
service (DOS) because the PerpetualVault is incorrectly marked as open while the GMX position is
closed, causing those calls to repeatedly fail.

## Recommendation
The GmxUtils contract should set the savedCallbackContract so the afterOrderExecution function in
the GmxUtils contract is called during ADLs or liquidations. Additionally the validCallback modiﬁer
should allow the AdlHandler to call the GmxUtils contract for the current positionKey. The
afterOrderExecution function should also account for ADL calls from GMX.
This update should include a mechanism to transfer any funds sent to the GmxUtils contract due to
ADL to the PerpetualVault contract. Additionally, the afterOrderExecution function in the
PerpetualVault contract should check if the position is still open and handle the position decrease
accordingly.
If the position is closed, it should adjust the ﬂow to reﬂect that closure. It is also important to
consider the various ﬂows (deposit, signal change, withdraw, compound) that the vault can be in
during the PerpetualVault callback.
