# [M] UAIWT-2 | Fund Transfer From Wrapper Trader Can Be Skipped

## Summary
Severity: Medium
Contest weight: 0.1360
Dataset id: 20531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a user receives more GM than the minOutputAmount they set, the excess GM has to be deposited
into the Core protocol such that the Vault balance and Core balance align. However, this state
assumes _shouldSkipTransfer has been set to false upon deposit creation in the call to function
IsolationModeTokenVaultV1WithFreezable.executeDepositIntoVault:
else {
Require.that(
isVaultFrozen(),
_FILE,
"Vault should be frozen"
);
_setShouldVaultSkipTransfer(/* _shouldSkipTransfer = */ false);
}
It is possible to overwrite this pre-requisite state and set _shouldSkipTransfer = true through the
function UpgradeableAsyncIsolationModeUnwrapperTrader.callFunction when the sender is an
operator.
In this case, once the deposit is resolved and the afterDepositExecution callback is triggered, the
fund transfer into the Vault would be skipped and the funds would remain stuck inside the wrapper
trader.

## Recommendation
Prior to calling factory.depositIntoDolomiteMarginFromTokenConverter, explicitly
_setShouldVaultSkipTransfer(/* _shouldSkipTransfer = */ false);
