# [H] Prevent griefing attack on DebtManager.manualAllocation

## Summary
Severity: High
Contest weight: 0.2287
Dataset id: 6164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manual allocation will be always calculated based on a system state s. After the transaction gets minted there could be a completely new state s'.
An attacker could try to frontrun the manualAllocation transaction to produce a revert. There may be a financial incentive for the attacker to do so.
The manual allocation aims to optimize resource allocation by keeping only the minimum_total_idle amount, along with an optional buffer, in idle. An attacker could exploit this by withdrawing an amount equal to (buffer + 1) from the vault, thereby triggering a revert in the manualAllocation.
The revert in the manual allocation would happen in the vaultV3.update_debt function (see VaultV3.vy#L992).
A silo position debt_update would use all the remaining funds from the idle. The following silo debt_update position in the loop would revert because total_idle == minimum_total_idle.

## Recommendation
Add the following check to the manualAllocation loop.
// deposit/increase not possible because minimum total idle reached
if (position.debt > lenderData.current_debt && aggregator.totalIdle() == aggregator.minimum_total_idle()) continue;
