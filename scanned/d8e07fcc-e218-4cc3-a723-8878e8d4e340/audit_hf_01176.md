# [M] Incompatible Token Standard Handling in ERC20 Operations

## Summary
Severity: Medium
Contest weight: 0.2063
Dataset id: 5047
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Agent contract, ERC20 operations such as transfer, transferFrom, and approve rely on the assumption that the underlying token strictly adheres to the ERC20 standard, specifically by returning a boolean value. The contract uses the IERC20Metadata interface, which declares these functions with a returns (bool) signature. However, several widely-used tokens — most notably USDT (Tether) — deviate from the ERC20 standard by not returning a value or by reverting on failure silently, making them incompatible with this implementation.  
Consequently, any interaction with such tokens (e.g., fee claiming, liquidity provisioning via createLPPosition, or any approve operation) would result in a revert. This prevents the creation of an Agent with such tokens and blocks further functionality, limiting interoperability and creating unnecessary friction for users attempting to use popular non-compliant tokens.

Impact Explanation:  
High, because this issue completely blocks the functionality of the contract with non-standard tokens like USDT. Users will be unable to create agents, stake, or claim fees using such tokens, leading to failed interactions and degraded protocol usability. This limitation could also impact protocol adoption if users cannot use tokens they expect to work seamlessly.

## Recommendation
To improve compatibility and robustness, use OpenZeppelin’s SafeERC20 library for all ERC20 interactions. This library wraps token calls with checks that handle non-standard return behaviors safely. Additionally, refactor the contract interfaces to use IERC20 (without assuming the returns (bool) signature) and import the safeTransfer, safeTransferFrom, and safeApprove functions accordingly.  
This approach ensures safe interaction with both standard and non-standard tokens and minimizes the risk of revert due to non-compliance. Alternatively, implement a custom adapter layer or token wrapper that normalizes token behavior internally, though this adds complexity and is generally not needed if SafeERC20 is used correctly.
