Audit Report

## Title
Asymmetric Deposit-Limit Check Allows ETH Deposits to Exceed the Configured Cap - (File: contracts/LRTDepositPool.sol)

## Summary

`_checkIfDepositAmountExceedesCurrentLimit` uses structurally different comparisons for ETH vs. ERC-20 assets. The ETH branch omits the incoming `amount` from the comparison, allowing a depositor to push total ETH holdings above the configured `depositLimitByAsset` cap. The ERC-20 branch correctly blocks the same action by including `amount` in the comparison.

## Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` (lines 676–682):

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← no `amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← includes `amount`
}
```

When `totalAssetDeposits == depositLimit`, the ETH branch evaluates `100e18 > 100e18` → `false`, so `_beforeDeposit` does not revert and `depositETH` proceeds to mint rsETH and accept the ETH. The ERC-20 branch would evaluate `100e18 + amount > 100e18` → `true` and revert with `MaximumDepositLimitReached`.

This is further confirmed by the inconsistency with `getAssetCurrentLimit` (lines 402–409), which correctly returns `0` when `totalAssetDeposits == limit` (using subtraction), while the enforcement function fails to block deposits at that exact boundary.

Call chain:
```
depositETH(minRSETHAmountExpected, referralId)
  └─ _beforeDeposit(ETH_TOKEN, msg.value, minRSETHAmountExpected)   [L661]
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
            └─ returns false when totalAssetDeposits == depositLimit  ← bypass
```

## Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The deposit cap is a protocol-level risk-management invariant. Any user can call `depositETH` with an arbitrary `msg.value` at the exact moment `totalAssetDeposits == depositLimit`, bypassing the cap by up to `msg.value`. The protocol accepts ETH and mints rsETH beyond the intended ceiling. No direct fund theft occurs in a single transaction, but the invariant "total ETH deposits ≤ depositLimitByAsset(ETH)" is violated, which can compound with EigenLayer strategy capacity limits to produce downstream risk.

## Likelihood Explanation

Any unprivileged depositor can trigger this. The precondition — `totalAssetDeposits == depositLimit` — is a natural boundary condition that occurs whenever the pool approaches its cap. `depositETH` is a public payable function with no access control, reachable by any ETH holder without special privilege.

## Recommendation

Include the incoming deposit amount in the ETH branch, mirroring the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This aligns the enforcement logic with what `getAssetCurrentLimit` already reports and makes both code paths enforce the same invariant.

## Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 100 ether`.
2. Existing deposits bring `getTotalAssetDeposits(ETH_TOKEN)` to exactly `100 ether`.
3. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — the cap appears full.
4. Attacker calls `depositETH{value: 10 ether}(0, "")`.
5. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `100e18 > 100e18` → `false`. No revert.
6. `_mintRsETH` mints rsETH for the attacker; total ETH deposits become `110 ether`, 10% above the configured cap.
7. The equivalent ERC-20 call at the same boundary would revert: `100e18 + 10e18 > 100e18` → `true` → `MaximumDepositLimitReached`.

**Foundry fuzz test plan:**
```solidity
function testFuzz_ETHDepositBypassesCap(uint96 extraAmount) public {
    vm.assume(extraAmount > minAmountToDeposit);
    // fill pool to exactly the limit
    _fillETHToLimit();
    // assert getAssetCurrentLimit returns 0
    assertEq(pool.getAssetCurrentLimit(ETH_TOKEN), 0);
    // deposit should revert but does not
    vm.deal(attacker, extraAmount);
    vm.prank(attacker);
    pool.depositETH{value: extraAmount}(0, "");
    // total now exceeds limit
    assertGt(pool.getTotalAssetDeposits(ETH_TOKEN), lrtConfig.depositLimitByAsset(ETH_TOKEN));
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
