# [M] M-1 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.1269
Dataset id: 3123
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The project exhibits a centralized structure, primarily under the control of the owner, who possesses the ability to withdraw the project's liquidity in a single transaction. Additionally, other components within the project possess excessive control, posing further risks to users' funds. Notably:
• Strategies can mint arbitrary amounts of the aETH tokens.
• Tokens deposited in strategies may not be returned.
• RewardOracle features a centralized design, increasing the risk of inaccurate reporting.
• The aETH token may have multiple managers, implying that entities other than the CorePrimary contract might have minting rights.
This issue is rated as medium since there are multiple centralized points of vulnerability within the project, each of which requires precise management and security measures.

## Recommendation
To mitigate these risks, it is advised to implement Multisig accounts for each governance-related address, ensuring a more distributed and secure control mechanism.
