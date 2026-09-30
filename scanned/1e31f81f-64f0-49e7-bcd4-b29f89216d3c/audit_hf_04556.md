# [H] H-02 | Whitelist Actions Should Update All Vaults

## Summary
Severity: High
Contest weight: 0.2918
Dataset id: 22159
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Asset availability changes during whitelistDeposit and whitelistWithdraw. But, in these functions only the vault that is calling is updated with _updateAssetMetadataFromVault. Instead, all whitelisted vaults should be updated too which affects their interest calculations. Consider this example: • LAV has 100 DAI • Two Vaults A & B, with a 100% and 50% max allocation from LAV respectively. • Vault A & B each have whitelist withdrawn 25 DAI, so A's utilization rate is 25 / 75 = 33% while B's is 25 / 50 = 50% • 1 day passes • A new borrower borrows 50 DAI from Vault A, so utilization rate increases from 33 to 100%. • Available assets are also reduced for vault B, its utilization rate will increase to 25 / 25 = 100% In the example above, the next time accrued interest in Vault B is calculated, it assumes a 100% utilization rate for the entire duration since the last update. Instead, it should have been a 50% utilization (lower interest rate) for 1 day and then the 100% utilization rate after the borrow from Vault A. Borrowers will therefore always be incorrectly charged for interest across all whitelisted vaults.

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/10/files#diff-9b515764e5f217eb4ac72af9e365401af40db3fdbe5866f6b288c42500738de2

## Recommendation
whitelistDeposit and whitelistWithdraw should update all vaults by calling both: _updateAssetMetadataFromVault(_vault) and _updateInterestAndMdInAllVaults(_vault)
