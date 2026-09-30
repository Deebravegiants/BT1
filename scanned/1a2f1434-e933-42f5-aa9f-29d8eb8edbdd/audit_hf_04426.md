# [M] M-02 | Vault Position Not Sum Of User Positions

## Summary
Severity: Medium
Contest weight: 0.1748
Dataset id: 21902
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function getFundingSince is not perfectly precise, such that the decay of two time deltas X and Y is not the same as the funding decay of one time delta X + Y. This is important since chargeFunding only updates the last update timestamp for the vault position, not user positions. Consider this scenario where there is only one open position: 1) 10 seconds pass. 2) Vault is charged funding for 10 second decay. 3) 200 more seconds pass. 4) Vault is charged funding for 200 second decay; User is charged funding for 210 second delay. 5) User sends request to close their position. Ultimately, the latest position of the vault is not aligned with the latest position of the user due to the imprecision of getFundingSince. The position the user can reduce is greater than the latest vault position, causing an underflow when performing vault.position -= _positionToReduce. This can be harmful in the case there are multiple open positions, and a single depositor is left hanging and unable to close their position. Note that this issue is also applicable to the vault.debt -= debtToReduce_; calculation as the debt is also updated when funding is charged.

## Recommendation
Change the reduction to: uint256 amtPosToReduce = vault.position < _positionToReduce - vault.position ? _positionToReduce : _positionToReduce; vault.position -= amtPosToReduce; uint256 amtDebtToReduce = vault.debt < debtToReduce_ - vault.debt ? debtToReduce_ : debtToReduce_; vault.debt -= amtDebtToReduce; bAsset.transfer(msg.sender, amtPosToReduce)
