# [H] MJR-1 Correct migration

## Summary
Severity: High
Contest weight: 0.2254
Dataset id: 16523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the strategy contract’s constructor, where it grants unlimited spend allowances (approve) for external token contracts such as CRV and USDC. These allowances are intended to enable the strategy to manage its assets while it is active. However, when the strategy is migrated to a new implementation, the migration routine does not revoke or reset those allowances. As a result, the old strategy contract retains the right to move the tokens that remain in its balance after migration. An attacker who can trigger a transferFrom call on the token contracts, or a malicious new strategy that re‑uses the old allowance, can drain the assets that were supposed to be transferred to the new strategy. The impact is that users who have deposited funds into the vault may see their balances reduced or completely emptied after a migration that appears to have succeeded. The issue manifests only during or after a migration operation, specifically when the prepareMigration function is executed without clearing the previously granted approvals. Token holders, the vault’s governance, and any downstream protocol that relies on the migrated strategy are affected because the accounting assumptions that the old contract no longer has control over the assets are violated. The flaw was discovered during a manual security audit performed by MixBytes, which noted that the constructor’s approve calls were never paired with a corresponding reset in the migration path. Because approvals are stored on the token contracts and not reflected in the strategy’s UI, the problem can be difficult to notice; the migration may look successful while the hidden allowance still exists. To remediate the issue, the migration routine should explicitly set the allowances for all previously approved tokens back to zero, claim any pending rewards, transfer any residual token balances to the new strategy, and finally revoke the vault’s own approvals. This ensures that after migration the old contract no longer possesses any authority to move user funds, restoring the intended accounting invariants and preventing unauthorized token transfers.

## Recommendation
It is recommended to add in function prepareMigration():
```solidity
IERC20(crv).safeApprove(address(want), 0);
IERC20(usdc).safeApprove(sushiswap, 0);
IyveCRV(address(want)).claim();
want.safeTransfer(_newStrategy, want.balanceOf(address(this)));
IERC20(usdc).safeTransfer(_newStrategy, IERC20(usdc).balanceOf(address(this)));
want.safeApprove(vault, 0);
vault.approve(rewards, 0);
```
