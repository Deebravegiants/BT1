# [M] M-01 | Collateral Lost When Combining Swaps

## Summary
Severity: Medium
Contest weight: 0.1702
Dataset id: 2395
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation allows both external calls and internal swaps to be executed in the same transaction. Users can externally swap tokens and send them to orderVault as collateral, and later use atomic swaps to receive WNT in order to pay the execution and relay fees.

However, the unrecorded collateral in the orderVault is at risk if the atomic swap uses the same collateral for tokenIn. The following scenario could occur:
• User swaps ARB for USDC in external calls, sends USDC to orderVault.
• User swaps USDC to WNT using atomic swap, sending USDC to orderVault, and later executing SwapUtils.swap
• Now createOrder is triggered, and collateral is recorded with recordTransferIn
• cache.initialCollateralDeltaAmount will be 0, and user lost the USDC collateral

The issue relies on the fact that orderVault is a StrictBank, so when SwapUtils.swap calls params.bank.transferOut it also triggers _afterTransferOut, syncing the tokenBalances with the current bank balance (which includes the user's collateral).

## Proof of Concept
https://github.com/GuardianOrg/gmx-synthetics-team2/blob/audit-rems/test/router/relay/GelatoRelayRouter.ts#L785

## Recommendation
Prevent users from combining external calls and internal atomic swaps within the same transaction, either through the UI or by implementing on-chain protections.
