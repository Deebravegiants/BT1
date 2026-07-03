The code matches the claim exactly. The bug is confirmed real.

- Line 679: ETH branch uses `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` (strict `>`)
- Line 681: ERC-20 branch uses `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)` (correctly includes `amount`)
- Line 404: `getAssetCurrentLimit` uses `>` for the zero-return check, so when `totalAssetDeposits == limit`, it returns `0` — but the enforcement gate still admits the deposit

The inconsistency is concrete and exploitable by any unprivileged depositor.

---

Audit Report

## Title
ETH Deposit Limit Not Enforced at Exact Boundary Due to Strict Inequality - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses a strict `>` comparison for the ETH branch, meaning when `totalAssetDeposits` equals exactly `depositLimitByAsset(ETH_TOKEN)`, the check returns `false` and the deposit is not reverted. This allows any depositor to push ETH deposits beyond the configured cap at the exact boundary, while the public view `getAssetCurrentLimit` already reports zero remaining capacity at that same state.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the ETH branch of `_checkIfDepositAmountExceedesCurrentLimit` evaluates:

```solidity
return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));  // line 679
```

When `totalAssetDeposits == depositLimit`, this expression is `false`, so `_beforeDeposit` (lines 661–663) does not revert and the deposit proceeds. The ERC-20 branch on line 681 correctly includes `amount` in the comparison (`totalAssetDeposits + amount > limit`), so a zero-remaining-capacity state blocks further ERC-20 deposits. The ETH branch has no such protection. Meanwhile, `getAssetCurrentLimit` (lines 402–409) uses the same `>` threshold and returns `depositLimit - totalAssetDeposits = 0` when the two are equal — creating a directly observable inconsistency between the public view (reports 0 capacity) and the enforcement gate (admits deposits).

## Impact Explanation
An unprivileged depositor calling `depositETH` when `totalAssetDeposits == depositLimit` bypasses the protocol's ETH deposit cap and causes rsETH to be minted against ETH that exceeds the configured ceiling. No funds are stolen, but the protocol fails to enforce its stated deposit constraint. This matches **Low — contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation
The boundary condition is reachable in two realistic ways: (a) an admin sets `depositLimitByAsset(ETH_TOKEN)` to exactly the current TVL to freeze new deposits — immediately exploitable by any depositor — or (b) a natural sequence of deposits lands the total at the limit. No special privileges or victim mistakes are required; any external caller can trigger it by sending ETH via `depositETH`.

## Recommendation
Change the strict inequality to `>=` in the ETH branch of `_checkIfDepositAmountExceedesCurrentLimit` (line 679):

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits >= lrtConfig.depositLimitByAsset(asset));
}
```

This aligns the enforcement gate with `getAssetCurrentLimit`, which already treats `totalAssetDeposits == depositLimit` as zero remaining capacity.

## Proof of Concept
1. Admin calls `lrtConfig.setDepositLimitByAsset(ETH_TOKEN, X)` where `X` equals the current `getTotalAssetDeposits(ETH_TOKEN)`.
2. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — cap is reported as full.
3. Depositor calls `depositETH{value: 1 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `X > X` → `false` → no revert.
5. `_mintRsETH` mints rsETH for the depositor; total ETH deposits become `X + 1 ether`, exceeding the configured limit.
6. Repeat indefinitely — each subsequent call also passes the `>` check until `totalAssetDeposits` strictly exceeds `X`.