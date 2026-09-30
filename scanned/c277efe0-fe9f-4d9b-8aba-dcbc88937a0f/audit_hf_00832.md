# [M] M-03 | Collateral Locks Are Not Cleared On Liquidation

## Summary
Severity: Medium
Contest weight: 0.1094
Dataset id: 2568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a migration happens, all of the user's collateral in escrows in v2 is locked in the v3 system, which means that it can be delegated, but not withdrawn. These locks are not cleared on account liquidation. So if a user gets liquidated and deposits new collateral back into the same account afterwards, the unexpired locks will still prevent them from withdrawing this new collateral. The same applies to vault liquidations. This may be unexpected for users and result in unexpected locked funds as a result of their previous locks in the V2 system, which should not apply to new collateral they deposit directly into V3.

## Recommendation
When an account liquidation happens, iterate over the account's locks and deduct the liquidated amount from them. However, this will not work for vault liquidations because there will be many users in a vault. Either implement a different lock mechanism or document this risk.
