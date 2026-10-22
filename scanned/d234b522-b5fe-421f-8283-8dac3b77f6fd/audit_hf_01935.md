# [M] Incorrect Receipt Token Minting for Fee on Transfer Tokens

## Summary
Severity: Medium
Contest weight: 0.1728
Dataset id: 10678
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MultipliBridger contract’s deposit mechanism fails to properly account for fee-on-transfer (FoT) tokens. The vulnerability manifests in the deposit function, which invokes TransferHelper.safeTransferFrom(token, msg.sender, address(this), amount) to transfer tokens from the user to the contract. This implementation assumes the amount specified will exactly match the tokens received by the contract, which is incorrect for FoT tokens that deduct a transfer fee. The contract then emits the BridgedDeposit event with the full pre-fee amount as the deposited value. Off-chain systems, including the sequencer and bridging back-end that monitor these events, will interpret this logged amount as the actual value received by the contract. This creates a discrepancy where users receive receipt tokens ( xTokens on L2 ) based on the pre-fee amount while the contract holds less value than recorded. When FoT tokens are deposited, the protocol will credit users with receipt tokens based on the pre-fee amount while holding less actual token value in the contract. This creates an accounting imbalance that could lead to liquidity shortfalls when processing withdrawals.

## Recommendation
The contract should implement FoT token handling by comparing the balance before and after transfers. For the deposit function, first record the contract’s token balance, then perform the transfer, then verify the new balance to determine the actual received amount.
