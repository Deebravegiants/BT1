# [C] Reentrancy in groupMint() allows unlimited group token minting via malicious treasury callback

## Summary
Severity: Critical
Chain: Smart contract
Component: Circles
Published: 2026-03-22
Source: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/124
Type: hats-finding

## Details
## Severity: CRITICAL — Unlimited Token Minting

## Description

The `Hub.groupMint()` function (line 419) lacks a reentrancy guard, while `operateFlowMatrix()` (line 546) has `nonReentrant(0)`. A malicious treasury contract can exploit this by reentering `groupMint()` during the `onERC1155BatchReceived` callback, minting unlimited group Circles from a single collateral deposit.

## Root Cause

In `_groupMint()`:
- Line 726: `safeBatchTransferFrom(_sender, treasuries[_group], ...)` — external call to treasury, triggers `onERC1155BatchReceived`
- Line 729: `_mintAndUpdateTotalSupply(...)` — group Circles minted AFTER the external call

When the treasury reenters `groupMint()`, it becomes `msg.sender`. The `safeBatchTransferFrom(treasury, treasury, ...)` is a self-transfer that does NOT consume the collateral. But `_mintAndUpdateTotalSupply` still mints group Circles. Each reentry multiplies the minted amount.

## Attack Steps

1. Attacker deploys malicious treasury contract and permissive mint policy
2. Attacker calls `registerGroup()` with malicious treasury and mint policy
3. Attacker sets trust: group trusts the collateral avatar
4. Attacker calls `groupMint()` with N units of collateral
5. Hub transfers collateral to malicious treasury (line 726)
6. Treasury's `onERC1155BatchReceived` reenters `groupMint()` with same params
7. In reentrant call: `safeBatchTransferFrom(treasury, treasury, ...)` = self-transfer, collateral stays
8. `_mintAndUpdateTotalSupply` mints N more group Circles
9. Repeat steps 6-8 for K reentries → K*N extra group tokens minted
10. Total: (K+1)*N group Circles from N collateral

## Impact

- **Unlimited group token inflation** from single collateral deposit
- Attacker can mint arbitrary amounts of group Circles
- If the group's Circles have value (traded, trusted by others), attacker extracts that value
- Devalues all existing holders of the group's Circles
- In established groups with trust relationships, this can drain value from all members

## Proof of Concept

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/124_
