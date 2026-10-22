# [M] M-22 | Missing Storage Gaps

## Summary
Severity: Medium
Contest weight: 0.0347
Dataset id: 2556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the absence of reserved storage gaps in an upgradeable smart contract that inherits from a token standard implementation. In proxy‑based upgrade patterns, the storage layout of the implementation contract must remain compatible across upgrades. The root cause is that the base ERC6909 contract does not declare a placeholder array (commonly called a storage gap) to occupy unused storage slots. When a future upgrade adds, removes, or reorders state variables in either the base contract or a derived contract, the new variables will be written to storage slots that were previously occupied by existing variables. This misalignment corrupts the contract's storage, causing values such as token balances, allowance mappings, or configuration parameters to be overwritten or shifted. An attacker who can trigger an upgrade that introduces new state variables could exploit the corrupted layout to manipulate balances, drain funds, or cause accounting errors. Even without a malicious upgrade, an honest developer who later adds a variable to the contract may unintentionally overwrite critical data, leading to unexpected zero balances, failed refunds, or loss of user funds. The impact is therefore a breach of the protocol’s accounting guarantees, potential loss of user assets, and a breakdown of the pool’s business logic. The issue manifests only when the contract is upgraded or when its inheritance hierarchy is changed; during normal operation the contract appears functional, making the problem hard to notice until a new version is deployed. The vulnerability was identified during a manual audit that examined the inheritance chain and noted the missing storage gap pattern. To remediate, the ERC6909 implementation should reserve a set of unused storage slots (for example, `uint256[50] private __gap;`) and any future contracts in the hierarchy should maintain or extend this gap when adding new state variables. This ensures that subsequent upgrades can introduce new variables without colliding with existing storage, preserving the integrity of balances and other critical state. The bug belongs to the class of upgradeable‑contract storage‑collision vulnerabilities, where missing storage gaps lead to corrupted state and unintended behavior such as funds disappearing or refunds failing.

## Recommendation
Consider adding storage gaps in the ERC6909 contract.
