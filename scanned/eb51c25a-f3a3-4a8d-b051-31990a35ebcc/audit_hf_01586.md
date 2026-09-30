# [H] MJR-8 Unnecessary allowance

## Summary
Severity: High
Contest weight: 0.0073
Dataset id: 8506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an unnecessary ERC20 allowance being granted by the vault contract during a withdrawal operation. In the YearnV2 implementation the withdraw function is designed to burn the caller’s share tokens rather than transfer the underlying asset, which means the contract never needs to move ERC20 tokens on behalf of the user. However, the code still calls the token’s approve method and sets an allowance for the vault to spend the user’s tokens. The root cause is a logical mismatch: the developer assumed a transfer would be required and therefore added an allowance, but the actual business logic only burns shares. Because the allowance remains active, any address that can call the token’s transferFrom function with the vault’s allowance can move the underlying tokens out of the vault without the user’s consent. An attacker who obtains the allowance (for example by being the vault or by exploiting a separate contract that can invoke transferFrom) can drain the vault’s token balance, resulting in loss of funds for all depositors. This issue manifests whenever a user initiates a withdrawal; the contract silently creates an allowance that is never used for the intended burn operation, exposing the token balance to potential misuse. All users who have deposited tokens into the vault, as well as the protocol that relies on the vault’s accounting, are affected because the unexpected allowance breaks the assumption that only the vault can manage its own assets. The problem was discovered during a manual security audit that compared the withdraw logic with the allowance handling and identified the redundant approve call. It can be hard to notice because the approve call does not produce an immediate error and the allowance may appear harmless in normal operation, yet it opens a hidden attack surface. To remediate the issue, the contract should stop granting any ERC20 allowance during withdrawal, removing the approve call entirely, or ensure that no external address can invoke transferFrom with that allowance. This aligns the implementation with the intended accounting model where shares are burned and no token transfer is required, eliminating the risk of unauthorized token movement and preserving the integrity of user balances.

## Recommendation
We recommend removing providing allowance.
