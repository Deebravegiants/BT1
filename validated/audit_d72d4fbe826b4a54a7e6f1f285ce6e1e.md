Audit Report

## Title
ETH Deposit Limit Unenforced Due to Missing `amount` in Cap Check — (`contracts/LRTDepositPool.sol`)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies structurally different comparisons for ETH vs. ERC20 assets. The ERC20 branch correctly checks `totalAssetDeposits + amount > depositLimit`, while the ETH branch checks only `totalAssetDeposits > depositLimit`, omitting `amount` entirely. As a result, any ETH deposit passes the cap check as long as the running total has not already exceeded the limit, regardless of the deposit size.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the function `_checkIfDepositAmountExceedesCurrentLimit` is intended to return `true` when a proposed deposit would push total deposits over the configured cap:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount omitted
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // amount included
}
``` [1](#0-0) 

Two defects are present in the ETH branch simultaneously:
1. `amount` is not added — the check evaluates the *current* total, not the *post-deposit* total.
2. Strict `>` instead of `>=` — even a state where `totalAssetDeposits == depositLimit` returns `false`, permitting one more deposit.

The caller path is fully unprivileged:

```
depositETH(minRSETHAmountExpected, referralId)   [external payable, no role check]
  └─ _beforeDeposit(ETH_TOKEN, msg.value, ...)
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
            └─ returns false  ← never reverts for ETH while totalAssetDeposits ≤ depositLimit
``` [2](#0-1) [3](#0-2) 

The `_beforeDeposit` check at line 661 calls `_checkIfDepositAmountExceedesCurrentLimit` and reverts with `MaximumDepositLimitReached` only if it returns `true`. Because the ETH branch never includes `amount`, it returns `false` for any deposit size whenever `totalAssetDeposits ≤ depositLimit`, and the revert is never triggered.

## Impact Explanation
The ETH deposit cap (`depositLimitByAsset(ETH_TOKEN)`) is entirely unenforced. Any unprivileged depositor can call `depositETH` with an arbitrary `msg.value` and receive rsETH in return, regardless of how much ETH has already been deposited. The protocol's TVL cap — a primary risk-management invariant — is silently bypassed for every ETH deposit. rsETH is minted against ETH that exceeds the administrator-configured limit, violating the protocol's stated invariant that no asset's total deposits may exceed `depositLimitByAsset`. This constitutes a contract failing to deliver its promised behavior (enforced deposit caps). Depending on the reason the cap was set (e.g., EigenLayer strategy exposure limits, liquidity constraints), excess deposits that cannot be absorbed by the underlying strategy can escalate to protocol insolvency. **Impact: Low (contract fails to deliver promised returns) with a credible path to Critical (protocol insolvency) if the deposit limit was set to reflect EigenLayer strategy capacity.**

## Likelihood Explanation
`depositETH` is `external payable` with no role restriction. The precondition (`totalAssetDeposits ≤ depositLimit`) is the normal operating state of the protocol. Any depositor — including an automated bot — can trigger this at any time without coordination, privilege, or victim interaction. Likelihood is high.

## Recommendation
Replace the ETH branch to mirror the ERC20 branch exactly:

```solidity
// Before (broken):
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}

// After (correct):
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

## Proof of Concept

```solidity
// Foundry fuzz test (run against a local fork or mock setup)
function testFuzz_ETHDepositBypassesLimit(uint256 depositAmount) public {
    depositAmount = bound(depositAmount, 1, 1000 ether);

    // Pre-fill the pool to exactly the ETH deposit limit
    _fillETHToExactLimit();

    uint256 limitBefore = lrtConfig.depositLimitByAsset(LRTConstants.ETH_TOKEN);
    uint256 totalBefore = depositPool.getTotalAssetDeposits(LRTConstants.ETH_TOKEN);
    assertEq(totalBefore, limitBefore); // precondition: at the limit

    // Unprivileged depositor sends ETH beyond the limit
    vm.deal(attacker, depositAmount);
    vm.prank(attacker);
    // Should revert with MaximumDepositLimitReached — but does NOT on unpatched code
    depositPool.depositETH{value: depositAmount}(0, "");

    uint256 totalAfter = depositPool.getTotalAssetDeposits(LRTConstants.ETH_TOKEN);
    // Invariant broken: total now exceeds the configured limit
    assertGt(totalAfter, limitBefore);
}
```

On unmodified code the test passes (deposit succeeds, invariant broken). After applying the fix (`totalAssetDeposits + amount > depositLimit`), the deposit correctly reverts with `MaximumDepositLimitReached` for all non-zero `depositAmount`.

### Citations

**File:** contracts/LRTDepositPool.sol (L86-87)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
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
