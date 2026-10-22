# [M] Losses are not distributed equally

## Summary
Severity: Medium
Contest weight: 0.1976
Dataset id: 20296
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Assume that three (3) destination vaults (DVs) and the withdrawal queue are arranged in this order: DVA, DVB, DVC. Assume the following appreciation and depreciation of the price of the underlying LP tokens of the DV:
• Underlying LP Tokens of DVA appreciate 5% every T period (Vault in Profit)
• Underlying LP Tokens of DVB depreciate 5% every T period (Vault in Loss)
• Underlying LP Tokens of DBC depreciate 10% every T period (Vault in Loss)
For simplicity's sake, all three (3) DVs have the same debt value. In the current design, if someone withdraws the assets, they can burn as many DVA shares as needed since DVA is in profit. If DVA manages to satisfy the withdrawal amount, the loop will stop here. If not, it will move to DVB and DBC to withdraw the remaining amount. However, malicious users (also faster users) can abuse this design. Once they notice that LP tokens of DVB and DVC are depreciating, they could quickly withdraw as many shares as possible from the DVA to minimize their loss. As shown in the chart below, once they withdrew all the assets in DVA at T14, the rest of the vault users would suffer a much faster rate of depreciation (~6%). Thus, the loss of the LMPVault is not evenly distributed across all participants. The faster actors will incur less or no loss, while slower users suffer a more significant higher loss. The losses are not distributed equally, leading to slower users suffering significant losses.

## Recommendation
Consider burning the shares proportionately across all the DVs during user withdrawal so that loss will be distributed equally among all users regardless of the withdrawal timing.
