# [M] M-08 | Centralization Issues

## Summary
Severity: Medium
Contest weight: 0.1580
Dataset id: 2029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ExitVaultEntryPoint contract grants the admin extensive control, posing significant centralization risks. Specifically, the rescueFunds function allows the admin to withdraw arbitrary tokens from any vault under the contract's management, including user-deposited assets and accrued rewards such as GMX and WETH. This enables the admin to transfer user funds without consent. Additionally, the admin has the authority to upgrade the implementation of the ExitVault contract via the UpgradeableBeacon. While intended for enhancements and bug fixes, this upgradability feature allows the admin to deploy malicious implementations that could manipulate user balances or drain assets across all existing vaults. Together, these privileges place excessive trust in a single admin, increasing the risk of unauthorized fund withdrawals and malicious activities that could compromise the entire protocol and its users.

## Recommendation
To mitigate centralization risks, it is essential to implement stricter access controls and limitations on the admin's privileges. For the rescueFunds function, restrict withdrawals to specific tokens that are not associated with user deposits or rewards and incorporate additional checks to prevent unauthorized access to user assets. Regarding contract upgrades, adopt a decentralized governance mechanism, such as a multi-signature wallet or a DAO governance model, to require consensus among multiple trusted parties before any upgrade can be executed.
