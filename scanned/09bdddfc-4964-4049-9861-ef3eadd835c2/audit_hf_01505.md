# [M] M-19 Claiming could be blocked

## Summary
Severity: Medium
Contest weight: 0.0351
Dataset id: 7996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements a claim mechanism that allows users to withdraw earned tokens after an athlete has transferred tokens to the distribution pool. The manager can invoke a function (lines 316‑337) that updates internal distribution state but does not call addDistributionAmount, which is responsible for crediting pending earnings. Because the pending earnings are never recorded, the condition that permits a claim remains false for users who had a claimable balance before the manager call. As a result, those users are forced to wait indefinitely until the athlete performs another token transfer that triggers the missing accounting update. The root cause is an incomplete state transition: the manager‑only function modifies distribution totals without updating the per‑user earnings mapping, effectively blocking the claim path. An attacker with manager privileges can deliberately invoke this function to freeze user withdrawals, causing funds to appear stuck and users to see a claim button that reverts or returns zero. The issue manifests only after the manager function is called and before any subsequent athlete token transfer, so it may be missed during normal testing where the sequence is not exercised. It affects all participants with pending rewards, breaking the business logic that rewards should be claimable immediately after they are earned. The problem was identified during a manual audit that traced the claim flow and noticed that the distribution‑total update does not propagate to the earnings accounting. The bug is subtle because the UI still shows a claim option, but the transaction fails silently, leading users to think their funds have disappeared. The appropriate fix is to invoke addDistributionAmount inside both updateDistribtionTotalEarningsAmounts() and updateDistributionEventCollectionIds() so that the earnings ledger is correctly updated whenever the manager changes distribution parameters, restoring the ability for users to claim their rewards without waiting for an extra token transfer.

## Recommendation
We recommend calling addDistributionAmount in the updateDistribtionTotalEarningsAmounts() and updateDistributionEventCollectionIds functions.
