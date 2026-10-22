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
// Foundry test — PASSES, showing 11x inflation
// 1000 collateral → 11,000 group tokens (1 + 10 reentries)

function test_ReentrancyMintUnlimited() public {
    treasury.setAttackParams(group, collateralId, 1000e18, 10);

    vm.prank(attacker);
    hub.groupMint(group, collateralId, 1000e18);

    assertEq(hub.totalGroupMints(), 11_000e18); // 11x inflation
    // Reentrancy count: 10
    // Inflation factor: 11 (unlimited with more reentries)
}
```

**Test output:**
```
[PASS] test_ReentrancyMintUnlimited()
  Attacker collateral before: 1000.000000000000000000
  Total group tokens minted:  11000.000000000000000000
  Collateral used:            1000.000000000000000000
  Inflation factor:           11
```

## Recommendation

Add `nonReentrant` modifier to `groupMint()`:
```solidity
function groupMint(...) external nonReentrant(1) {
```

Or follow checks-effects-interactions: mint group Circles BEFORE the safeBatchTransferFrom to treasury.

## Affected Code
- `src/hub/Hub.sol` line 419-430 (groupMint — missing nonReentrant)
- `src/hub/Hub.sol` line 726 (safeBatchTransferFrom to treasury — external call before mint)
- `src/hub/Hub.sol` line 729 (_mintAndUpdateTotalSupply — state update after external call)

## Payment Address
0x272e216c32ddab93d46929667A38E7F1f277620D
