# [H] Ownercan chain admin calls for same-block drains

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23272
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol’s admin controls let the owner chain privileged calls across the vault and wrapper in a single transaction:
• Vault path: Call SherpaVault::setStableWrapper to switch which token is protected from rescue. Then immediately call SherpaVault::rescueTokens to withdraw any balance of the old wrapper from the vault.
• Wrapper operator path: Call SherpaUSD::setOperator, then (as operator) use SherpaUSD::transferAsset to move USDC out of the wrapper.
• Wrapper keeper path: Call SherpaUSD::setKeeper, then use SherpaUSD::depositToVault to pull USDC from users who left approvals, mint SherpaUSD to the keeper, and extract value via the transferAsset path above.
All of these are owner‑only and have no built‑in delay, so they can be executed together in the same block.
Impact: Even though the code comments stress limiting owner power, the owner (or a compromised key) can immediately redirect custody and move funds with no user warning or reaction time. This creates a trust gap between stated intent and actual authority.

## Recommendation
Recommended Mitigation: * Add a delay (at least one withdrawal epoch) to SherpaVault.setStableWrapper, SherpaVault.rescueTokens, SherpaUSD.setOperator, SherpaUSD.setKeeper, and consider delaying SherpaUSD.transferAsset.
• Make SherpaVault.stableWrapper, SherpaUSD.keeper immutable.
• Use a timelock (e.g., OpenZeppelin TimelockController) with a user‑protective delay so people can withdraw or reduce approvals before changes take effect.
Sherpa:
6
Vault path: Call SherpaVault::setStableWrapper to switch which token is protected from rescue. Then immediately call SherpaVault::rescueTokens to withdraw any balance of the old wrapper from the vault.
Wrapper keeper path: Call SherpaUSD::setKeeper, then use SherpaUSD::depositToVault to pull USDC from users who left approvals, mint SherpaUSD to the keeper, and extract value via the transferAsset path above.
We're implementing a pseudo‑immutable stableWrapper and keeper - both will be set once during deployment and cannot be changed after system initialization. This eliminates both attack surfaces while maintaining the deployment flexibility needed to solve the chicken‑and‑egg deployment problem: vault constructor requires wrapper address, but we can't deploy wrapper until vault exists. We solve this by deploying vault with a temporary wrapper address, then calling setStableWrapper() once to set the real wrapper and lock it permanently.
Wrapper operator path: Call SherpaUSD::setOperator, then (as operator) use SherpaUSD::transferAsset to move USDC out of the wrapper.
Timelocks / delays on setOperator and related admin functions would be ineffective given our vault's trust model and architecture. The operator already has manual custody of strategy funds (transferred to fund manager for on and off‑chain strategy delegation) and can pause the system at will, meaning any timelock delay could be circumvented by simply pausing withdrawals during the timelock window. The operator must remain changeable for operational flexibility (personnel changes, key rotation) so we cant make it immutable like we did with keeper and setStableWrapper. The owner role is a 2‑of‑3 multisig that controls operator selection, so centralization is lessened there as best as we can.
