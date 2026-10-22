# [M] rate should be updated before modifyCollater

## Summary
Severity: Medium
Contest weight: 0.1341
Dataset id: 17617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the user is not calling through VaultActions, vaults[vault].rate will not be updated before modifyCollateralAndDebt(), thus repayment can be made at a lower rate than expected.  
At L124 in VaultActions.sol, publican.collect(vault) will be called to update vaults[vault].rate of codex with codex.modifyRate().  
However, the user may not repay their debt using VaultActions but interact with the codex contract directly.  
By doing so, codex.modifyCollateralAndDebt() will use the old rate, which should be updated with publican.collect(vault).  
If vaults[vault].rate is not updated by others, then the user can avoid the interests since the last updated time.

## Recommendation
The same problem also exists in MakerDAO.  
Seems like MakerDAO has realized this issue and set up a keeper bot to call drip() from time to time and update the rate: https://etherscan.io/address/0x0a51500250d1f6e2612a5d14d2094b5573635774  
This is expected and should not be labeled as 'high'. We have a service which collects the interest every 3 days as well on Gelato. In the worst case the protocol may loose out on a tiny amount of due interest, though on the other hand we don't have to resort for a more explicit interest accounting mechanism - which saves the users gas in the end. When Maker designed this mechanism they were aware of the tradeoffs.
