# [M] Incorrect collateral transferred leads to loss of user funds

## Summary
Severity: Medium
Contest weight: 0.1295
Dataset id: 17467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
setCollateralWrapper transfers the entire collateral from the user instead of transferring only the differential amount when there is already some previously deposited collateral. If setCollateralTo > currentPosition.collateral, then instead of transferring the differential collateral (i.e. setCollateralTo - currentPosition.collateral) amount from the user, setCollateralWrapper transfers the entire collateral amount of setCollateralTo again from the user. At a minimum, the user is surprised (could affect their protocol engagement) and the transaction could revert if the user doesn't have the unexpected amount of collateral funds. If transferred, it leads to the loss of the user's additional collateral to the protocol wrapper, which may be claimed by the next user engaging with the wrapper contract.

## Recommendation
Transfer only setCollateralTo - currentPosition.collateral instead of setCollateralTo. This has been resolved. https://github.com/lyra-finance/lyra-protocol/blob/avalon/contracts/LiquidityPool.sol#L454 Looks reasonable.
