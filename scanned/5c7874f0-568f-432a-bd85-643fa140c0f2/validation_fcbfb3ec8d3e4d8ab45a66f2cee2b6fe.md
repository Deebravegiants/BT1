Looking at the `withinUnstakeLimits` modifier and the full `LRTConverter.sol`, I can now trace the exact logic.

Now I have all the information needed for a complete analysis. Let me trace the exact logic.

---

### Title
`withinUnstakeLimits` Prematurely Drains `whitelistedUnstakeAllowance` When `availableActiveETHWithdrawals` Alone Covers the Unstake, Temporarily Freezing stETH in LRTConverter — (`contracts/LRTConverter.sol`)

### Summary

The `withinUnstakeLimits` modifier in `LRTConverter` always consumes from `whitelistedUnstakeAllowance` whenever it is non-zero, even when `availableActiveETHWithdrawals` (`assetsCommitted[ETH_TOKEN]`) alone is sufficient to authorize the unstake. After the ETH withdrawal queue is later unlocked and `assetsCommitted[ETH_TOKEN]` drops to zero, `whitelistedUnstakeAllowance` is also zero, so any subsequent `unstakeStEth` call reverts with `UnstakeLimitExceeded`, leaving newly-transferred stETH frozen in the converter until a whitelisted user manually calls `declareWithdrawalIntent`.

### Finding Description

The modifier at `LRTConverter.sol` lines 58–77:

```solidity
modifier withinUnstakeLimits(uint256 amountToUnstake) {
    uint256 availableActiveETHWithdrawals = _getActiveETHUserWithdrawals(); // reads assetsCommitted[ETH_TOKEN]

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
``` [1](#0-0) 

The **gate check** (line 65) correctly uses the sum `whitelistedUnstakeAllowance + availableActiveETHWithdrawals`. However, the **consumption logic** (lines 70–75) always deducts `min(amountToUnstake, whitelistedUnstakeAllowance)` from `whitelistedUnstakeAllowance` whenever it is non-zero — regardless of whether `availableActiveETHWithdrawals` alone was sufficient to authorize the call.

`availableActiveETHWithdrawals` is a live read of `lrtWithdrawalManager.assetsCommitted(ETH_TOKEN)`: [2](#0-1) 

`assetsCommitted[ETH_TOKEN]` is decremented inside `_unlockWithdrawalRequests` when the operator calls `unlockQueue`: [3](#0-2) 

**Exact exploit sequence (W=100, A=1000):**

| Step | Action | `whitelistedUnstakeAllowance` | `assetsCommitted[ETH_TOKEN]` |
|------|--------|-------------------------------|------------------------------|
| 0 | Initial state | 100 | 1000 |
| 1 | `unstakeStEth(100)` — gate: `100 ≤ 100+1000` ✓; consume: `min(100,100)=100` | **0** | 1000 |
| 2 | `unlockQueue(ETH_TOKEN,...)` processes all pending requests | 0 | **0** |
| 3 | `transferAssetFromDepositPool(stETH, X)` — new stETH arrives | 0 | 0 |
| 4 | `unstakeStEth(1)` — gate: `1 > 0+0` → **reverts `UnstakeLimitExceeded`** | 0 | 0 | [4](#0-3) 

The stETH transferred in step 3 is now frozen. The only recovery path is a whitelisted user calling `declareWithdrawalIntent`, which is an out-of-band user action not guaranteed to occur promptly: [5](#0-4) 

### Impact Explanation

stETH held in `LRTConverter` cannot be submitted to Lido's withdrawal queue by the operator. The assets are not lost permanently (a whitelisted user can unblock via `declareWithdrawalIntent`), but they are frozen for an indefinite period without any on-chain guarantee of timely resolution. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation

This is a normal operational sequence requiring no privileged compromise:
- A whitelisted user declares intent for `W` (routine)
- Users initiate ETH withdrawals totalling `A >> W` (routine)
- Operator unstakes a batch of `W` stETH (routine)
- Operator calls `unlockQueue` to process the ETH withdrawal queue (routine)
- New stETH is transferred to the converter (routine)

All five steps are expected production operations. The bug triggers silently with no warning.

### Recommendation

Prioritize consuming `availableActiveETHWithdrawals` before touching `whitelistedUnstakeAllowance`. Only deduct from `whitelistedUnstakeAllowance` the portion that `availableActiveETHWithdrawals` cannot cover:

```solidity
if (whitelistedUnstakeAllowance > 0 && availableActiveETHWithdrawals < amountToUnstake) {
    uint256 remainingAfterActive = amountToUnstake - availableActiveETHWithdrawals;
    uint256 whitelistedAmountConsumed =
        remainingAfterActive > whitelistedUnstakeAllowance
            ? whitelistedUnstakeAllowance
            : remainingAfterActive;
    whitelistedUnstakeAllowance -= whitelistedAmountConsumed;
}
```

This preserves `whitelistedUnstakeAllowance` when active ETH withdrawals already justify the operation.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode unit test (Foundry-style)
function test_whitelistedAllowanceDrainedByActiveWithdrawals() public {
    // Setup: W=100, A=1000
    vm.prank(whitelistedUser);
    converter.declareWithdrawalIntent(100 ether);          // whitelistedUnstakeAllowance = 100

    // Simulate assetsCommitted[ETH_TOKEN] = 1000 via user initiateWithdrawal calls
    _simulateETHWithdrawalCommitments(1000 ether);         // assetsCommitted[ETH_TOKEN] = 1000

    // Step 1: operator unstakes W=100; gate passes (100 <= 100+1000), consumes 100 from allowance
    vm.prank(operator);
    converter.unstakeStEth(100 ether);
    assertEq(converter.whitelistedUnstakeAllowance(), 0);  // allowance drained

    // Step 2: operator unlocks ETH withdrawal queue → assetsCommitted[ETH_TOKEN] = 0
    vm.prank(operator);
    withdrawalManager.unlockQueue(ETH_TOKEN, nextNonce, ...);
    assertEq(withdrawalManager.assetsCommitted(ETH_TOKEN), 0);

    // Step 3: new stETH transferred to converter
    vm.prank(assetTransferRole);
    converter.transferAssetFromDepositPool(stETH, 50 ether);

    // Step 4: operator cannot unstake — both limits are zero
    vm.prank(operator);
    vm.expectRevert(ILRTConverter.UnstakeLimitExceeded.selector);
    converter.unstakeStEth(1 ether);                       // stETH frozen
}
``` [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTConverter.sol (L170-177)
```text
    function unstakeStEth(uint256 amountToUnstake)
        external
        nonReentrant
        onlyLRTOperator
        withinUnstakeLimits(amountToUnstake)
    {
        _unstakeStEth(amountToUnstake);
    }
```

**File:** contracts/LRTConverter.sol (L216-227)
```text
    function declareWithdrawalIntent(uint256 amount) external nonReentrant onlyWhitelistedUser {
        if (amount == 0) {
            revert InvalidAmount();
        }
        uint256 maxWhitelistedAllowance = 1_000_000_000 ether;
        if (whitelistedUnstakeAllowance + amount > maxWhitelistedAllowance) {
            revert WhitelistedAllowanceExceeded();
        }

        whitelistedUnstakeAllowance = whitelistedUnstakeAllowance + amount;
        emit WithdrawalIntentDeclared(msg.sender, amount);
    }
```

**File:** contracts/LRTConverter.sol (L266-270)
```text
    function _getActiveETHUserWithdrawals() internal view returns (uint256 activeETHWithdrawals) {
        ILRTWithdrawalManager lrtWithdrawalManager =
            ILRTWithdrawalManager(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        activeETHWithdrawals = lrtWithdrawalManager.assetsCommitted(LRTConstants.ETH_TOKEN);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L800-803)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
```
