# [M] SetLimit does not take into account burned tokens

## Summary
Severity: Medium
Contest weight: 0.1005
Dataset id: 20451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function setLimit() may not be able to sufficiently restrict mint ability of
manager.
The setLimit() function reverts when newLimit_ < deployedOhm, mintOhmToVault
will revert if deployedOhm + amount_ > ohmLimit + circulatingOhmBurned. If the
value of circulatingOhmBurned is high, and the admin can only set the limit above
deployedOhm, they could end up in a state where they cannot limit the amount the
vault is allowed to burn sufficiently. I.e. the vault is always able to mint at least
circulatingOhmBurned new tokens.
so this value could grow arbitrarily high.
Lack of control of admin on mint ability of manager.

## Recommendation
Use similar restrictions as in mintOhmToVault() for setLimit or lower
circulatingOhmBurned when minting new OHM.
