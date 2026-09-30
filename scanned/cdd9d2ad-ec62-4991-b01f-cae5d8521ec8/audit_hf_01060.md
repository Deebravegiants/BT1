# [M] M-02 | Incorrect STETH Address

## Summary
Severity: Medium
Contest weight: 0.0419
Dataset id: 4045
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an incorrect reference to the stETH token contract within the protocol's configuration component. Instead of storing the address of the official stETH proxy contract (0xae7ab96520de3a18e5e111b5eaab095312d7fe84), the Config contract records the address of the underlying implementation contract (0x17144556fd3424EDC8Fc8A4C940B2D04936d17eb). This misconfiguration originates from a simple deployment or copy‑paste error where the developer selected the wrong contract artifact. Because the implementation contract does not expose the proxy’s expected external interface and does not hold any token balances, any operation that relies on the Config‑provided address—such as depositing, withdrawing, or querying stETH balances—will interact with a contract that cannot forward calls to the real token logic. Consequently, user‑initiated actions that appear to succeed on‑chain may result in no token transfer, zero balance updates, or silent failures, effectively making funds disappear from the user’s perspective. The issue manifests whenever the protocol reads the stETH address from Config, which occurs during normal user flows like staking, redemption, or fee calculation. All participants who hold or intend to move stETH through the platform—individual users, liquidity providers, and the protocol itself—are affected because the accounting assumptions that stETH balances are correctly tracked are violated. The flaw was uncovered during a manual audit of the contract configuration, where the auditor compared the stored address against the known proxy address and identified the mismatch. Detecting the problem is difficult because the stored address is syntactically valid, the contract compiles without warnings, and no explicit revert occurs; only the absence of expected token movement reveals the bug. To remediate, the Config contract should be updated to store the correct proxy address, ensuring that all downstream calls reach the proper stETH token contract and that balance updates reflect reality. This class of bug falls under misreferenced external contract addresses, a common source of functional failures in DeFi systems where proxy patterns are used.

## Recommendation
Update the STETH address to be the correct proxy address.
