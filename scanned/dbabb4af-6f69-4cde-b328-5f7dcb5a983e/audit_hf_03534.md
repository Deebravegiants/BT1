# [M] EXTH-1 | Lack of Contract Existence Check

## Summary
Severity: Medium
Contest weight: 0.0370
Dataset id: 19334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing contract‑existence verification before performing a low‑level call during the migration process. Because Solidity’s low‑level call returns a boolean that is true whenever the call does not revert, it also returns true when the target address contains no contract code. The root cause is that the migration contract assumes a true return value guarantees successful execution, but it does not check whether the callee actually exists. An attacker or a simple deployment mistake can cause the migration to invoke a non‑existent contract, for example when a token address is mistyped or the old contract has been self‑destructed. The call will succeed silently, the boolean will be true, and the migration logic will continue as if the external operation (such as a token transfer or state update) succeeded. Consequently, user funds may be sent to an address with no code and become unrecoverable, or the expected state change (e.g., balance update) will not happen. This situation occurs whenever the migration code uses low‑level .call or .call{value:…} without first confirming that address.code.length > 0. All users who rely on the migration to move their assets are affected, as are the protocol’s reputation and financial integrity. The issue was discovered during a manual audit that flagged the absence of an existence check. It is hard to notice because the transaction does not revert, no error event is emitted, and the UI may simply show a successful migration while the balance on the destination contract remains unchanged. The proper fix is to add a contract‑existence guard – for example, require(address(target).code.length > 0) – before any low‑level call, or to replace low‑level calls with interface calls that automatically revert when the target contract does not exist. This change ensures that a missing contract is detected early, preventing silent loss of funds and preserving the expected accounting logic of the migration.

## Recommendation
Consider implementing a contract existence check prior to the call.
