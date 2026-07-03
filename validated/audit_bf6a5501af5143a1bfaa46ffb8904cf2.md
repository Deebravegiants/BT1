### Title
`withinUnstakeLimits` Blocks `unstakeStEth` When Both Allowance Sources Are Zero — (`contracts/LRTConverter.sol`)

---

### Summary

The `withinUnstakeLimits` modifier in `LRTConverter` gates all `unstakeStEth` calls on the sum of `whitelistedUnstakeAllowance` and `assetsCommitted(ETH_TOKEN)`. When both are simultaneously zero — a reachable operational state — the operator cannot unstake any stETH regardless of how much stETH sits in the converter, causing a temporary freeze of those funds.

---

### Finding Description

The modifier enforces:

```solidity
if (amountToUnstake > whitelistedUnstakeAllowance + availableActiveETHWithdrawals) {
    revert UnstakeLimitExceeded();
}
``` [1](#0-0) 

where `availableActiveETHWithdrawals` is read directly from `LRTWithdrawalManager.assetsCommitted(ETH_TOKEN)`:

```solidity
activeETHWithdrawals = lrtWithdrawalManager.assetsCommitted(LRTConstants.ETH_TOKEN);
``` [2](#0-1) 

`assetsCommitted[ETH_TOKEN]` is incremented only when a user calls `initiateWithdrawal` for ETH:

```solidity
assetsCommitted[asset] += expectedAssetAmount;
``` [3](#0-2) 

and decremented during `_unlockWithdrawalRequests`:

```solidity
assetsCommitted[asset] -= request.expectedAssetAmount;
``` [4](#0-3) 

`whitelistedUnstakeAllowance` is only increased by whitelisted users calling `declareWithdrawalIntent`:

```solidity
whitelistedUnstakeAllowance = whitelistedUnstakeAllowance + amount;
``` [5](#0-4) 

and is consumed (decremented) inside the modifier itself on every successful `unstakeStEth` call:

```solidity
whitelistedUnstakeAllowance -= whitelistedAmountConsumed;
``` [6](#0-5) 

**Reachable blocking state:**

1. Operator calls `unstakeStEth` repeatedly, consuming all `whitelistedUnstakeAllowance` down to 0.
2. No new `declareWithdrawalIntent` is submitted by whitelisted users.
3. All pending ETH withdrawal requests are completed (or none were ever opened), so `assetsCommitted(ETH_TOKEN) = 0`.
4. Meanwhile, `transferAssetFromDepositPool` deposits additional stETH into the converter (this is the normal operational flow for funding unstaking).
5. Operator calls `unstakeStEth(any_amount > 0)` → reverts with `UnstakeLimitExceeded` for every non-zero amount.

The stETH is now stuck in the converter. `ethValueInWithdrawal` was already incremented when the stETH was transferred in:

```solidity
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
``` [7](#0-6) 

but the corresponding ETH can never be sent back to the deposit pool until the block is resolved, inflating the protocol's reported ETH value and rsETH price.

---

### Impact Explanation

- stETH held in `LRTConverter` cannot be unstaked to ETH, blocking the conversion pipeline needed to fulfill ETH withdrawal requests.
- `ethValueInWithdrawal` remains inflated, overstating total protocol assets and inflating the rsETH price reported by the oracle.
- The freeze persists until either: (a) the manager whitelists an address and that address calls `declareWithdrawalIntent`, or (b) users submit new ETH withdrawal requests. Neither happens automatically.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

This state arises through entirely normal operation with no attacker required:
- The operator legitimately depletes `whitelistedUnstakeAllowance` through normal `unstakeStEth` calls.
- A quiet period with no new ETH withdrawal requests (e.g., low user activity, all requests already fulfilled) leaves `assetsCommitted(ETH_TOKEN) = 0`.
- New stETH is deposited into the converter in anticipation of future unstaking.

No privilege escalation, key compromise, or external protocol failure is needed.

---

### Recommendation

Add a fallback path in `withinUnstakeLimits` (or a separate operator function) that allows unstaking when the converter holds stETH but both allowance sources are zero — for example, allow the operator to unstake up to the converter's actual stETH balance when `ethValueInWithdrawal > 0`. Alternatively, automatically replenish `whitelistedUnstakeAllowance` proportional to the stETH balance transferred in via `transferAssetFromDepositPool`.

---

### Proof of Concept

```solidity
// State setup:
// 1. whitelistedUnstakeAllowance = 0 (depleted by prior unstakeStEth calls)
// 2. assetsCommitted(ETH_TOKEN) = 0 (no pending ETH withdrawals)
// 3. stETH balance of LRTConverter > 0 (transferred via transferAssetFromDepositPool)

// Attempt to unstake:
vm.prank(operator);
lrtConverter.unstakeStEth(1 ether);
// Reverts: UnstakeLimitExceeded
// because: 1 ether > (0 + 0)

// Assert stETH is stuck:
assertGt(IERC20(stETH).balanceOf(address(lrtConverter)), 0);
// ethValueInWithdrawal is non-zero but ETH cannot be produced
assertGt(lrtConverter.ethValueInWithdrawal(), 0);
```

The modifier check at line 65 of `LRTConverter.sol` will always revert for any positive `amountToUnstake` when both sources are zero, confirming the freeze. [8](#0-7)

### Citations

**File:** contracts/LRTConverter.sol (L58-77)
```text
    modifier withinUnstakeLimits(uint256 amountToUnstake) {
        if (amountToUnstake == 0) {
            revert InvalidAmount();
        }

        uint256 availableActiveETHWithdrawals = _getActiveETHUserWithdrawals();

        if (amountToUnstake > whitelistedUnstakeAllowance + availableActiveETHWithdrawals) {
            revert UnstakeLimitExceeded();
        }

        // Consume intended withdrawal limit
        if (whitelistedUnstakeAllowance > 0) {
            uint256 whitelistedAmountConsumed =
                amountToUnstake > whitelistedUnstakeAllowance ? whitelistedUnstakeAllowance : amountToUnstake;

            whitelistedUnstakeAllowance -= whitelistedAmountConsumed;
        }
        _;
    }
```

**File:** contracts/LRTConverter.sol (L140-140)
```text
        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
```

**File:** contracts/LRTConverter.sol (L225-225)
```text
        whitelistedUnstakeAllowance = whitelistedUnstakeAllowance + amount;
```

**File:** contracts/LRTConverter.sol (L269-269)
```text
        activeETHWithdrawals = lrtWithdrawalManager.assetsCommitted(LRTConstants.ETH_TOKEN);
```

**File:** contracts/LRTWithdrawalManager.sol (L173-173)
```text
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L802-802)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
```
