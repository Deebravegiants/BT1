# [H] _badDebtMapping[collateral] can be unintentionally rewrite

## Summary
Severity: High
Reporter: BengalCatBalu
Contest weight: 0.0000
Dataset id: 4980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a storage mapping that records bad‑debt amounts for each collateral type, identified as _badDebtMapping[collateral]. The contract allows this mapping to be overwritten without proper authorization checks, meaning that any caller who can reach the function that writes to the mapping can replace the recorded bad‑debt value with an arbitrary number. The root cause is the absence of access control or validation on the write path, which turns a data‑integrity structure into a mutable field that can be tampered with. An attacker can exploit this by invoking the vulnerable function and setting the bad‑debt entry for a target collateral to zero, causing the protocol’s accounting logic to believe that no debt is outstanding. Consequently, the system may release the associated collateral to the attacker or prevent legitimate debt recovery, resulting in the loss of user funds. This impact is high because the protocol’s core financial guarantees rely on accurate bad‑debt tracking; corrupting the mapping breaks the accounting invariant that total collateral covers outstanding debt. The issue manifests whenever the contract’s update routine for bad debt is called, which, due to missing modifiers, can be triggered by any external address. All participants who deposit collateral or rely on the protocol’s debt‑settlement mechanism are affected, including lenders, borrowers, and the protocol itself. The flaw was discovered during a manual security audit performed by Spearbit, where the reviewer observed that the mapping variable was exposed and could be written to from a public function. Because the mapping appears to be a read‑only accounting table, developers may not notice that it can be altered, especially if the write function is buried in a larger codebase or lacks obvious naming. To remediate, the contract should enforce strict access control on any function that modifies the bad‑debt mapping, restrict writes to trusted roles (e.g., the protocol’s core logic contract), and add validation that prevents arbitrary values from being set. Additionally, separating the bad‑debt storage from user‑controlled inputs and employing immutable or private visibility can further protect the accounting integrity. In summary, the bug is a classic unauthorized state‑mutation vulnerability that enables an attacker to rewrite critical financial data, leading to potential fund disappearance and broken accounting guarantees.

## Recommendation
No data
