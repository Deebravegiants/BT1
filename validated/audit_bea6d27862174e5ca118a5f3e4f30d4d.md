### Title
Single Depositor Can Exhaust Entire `dailyMintLimit` in One Transaction, Blocking All Other Deposits for Up to 24 Hours — (`contracts/pools/RSETHPoolV2.sol`)

---

### Summary

The `limitDailyMint` modifier in `RSETHPoolV2` tracks a shared `dailyMintAmount` counter with no per-depositor cap. Any caller can deposit enough ETH in a single transaction to fill the entire daily limit, causing every subsequent `deposit()` call from any other user to revert with `DailyMintLimitExceeded` for up to 24 hours.

---

### Finding Description

`deposit()` applies the `limitDailyMint(msg.value)` modifier before executing. The modifier:

1. Computes `rsETHAmount` from the caller's ETH input.
2. Checks `dailyMintAmount + rsETHAmount > dailyMintLimit` — reverts if exceeded.
3. Otherwise increments `dailyMintAmount += rsETHAmount`. [1](#0-0) 

There is no per-depositor cap, no maximum single-deposit ceiling, and no mechanism to reserve capacity for other users. The only zero-check is `if (amount == 0) revert InvalidAmount()`, which runs *after* the modifier. [2](#0-1) 

An attacker can compute the exact ETH amount needed to set `dailyMintAmount == dailyMintLimit` in one call:

```
ethNeeded ≈ dailyMintLimit * rsETHToETHrate / 1e18  (adjusted for feeBps)
```

After that single deposit, `dailyMintAmount == dailyMintLimit`. Any subsequent deposit — even 1 wei — produces `rsETHAmount ≥ 1`, so `dailyMintAmount + rsETHAmount > dailyMintLimit` is true and the call reverts. The window lasts until `getCurrentDay()` increments (up to 24 hours). [3](#0-2) 

The daily reset only occurs when a new deposit is attempted on a new day — there is no keeper or automatic reset. [4](#0-3) 

---

### Impact Explanation

All users other than the attacker are unable to call `deposit()` for up to 24 hours. The attacker receives `wrsETH` in exchange for their ETH (no net loss of value, only capital lockup), making this a low-cost griefing attack. This matches **Medium — Temporary freezing of funds** (deposits are the only entry path for users on this L2 pool).

---

### Likelihood Explanation

- No special role or permission is required; `deposit()` is fully public.
- The attacker receives `wrsETH` back, so the only cost is opportunity cost on locked capital.
- The attack is repeatable every day.
- A coordinated group can split the ETH across multiple wallets to avoid detection.

---

### Recommendation

1. **Add a per-transaction deposit cap** (e.g., `maxSingleDepositAmount`) so no single call can consume more than a fraction of the daily limit.
2. **Or** enforce a per-address daily sub-limit so one address cannot exhaust the shared counter.
3. **Or** allow partial fills: instead of reverting when the limit would be exceeded, mint only up to the remaining limit and refund the excess ETH.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/pools/RSETHPoolV2.sol";

contract DailyLimitExhaustTest is Test {
    RSETHPoolV2 pool;
    address attacker = address(0xA);
    address victim   = address(0xB);

    function setUp() public {
        // Deploy/initialize pool with a known dailyMintLimit, e.g. 100 ether worth of rsETH
        // (mock oracle returning 1e18, feeBps = 0 for simplicity)
        // ... initialization omitted for brevity ...
    }

    function testExhaustDailyLimit() public {
        uint256 limit = pool.dailyMintLimit(); // e.g. 100e18 rsETH
        uint256 rate  = pool.getRate();        // e.g. 1e18 (1:1)

        // ETH needed to mint exactly `limit` rsETH (feeBps=0 → 1:1)
        uint256 ethNeeded = limit * rate / 1e18;

        vm.deal(attacker, ethNeeded);
        vm.prank(attacker);
        pool.deposit{value: ethNeeded}("ref");

        assertEq(pool.dailyMintAmount(), limit);

        // Victim cannot deposit any amount
        vm.deal(victim, 1 ether);
        vm.prank(victim);
        vm.expectRevert(RSETHPoolV2.DailyMintLimitExceeded.selector);
        pool.deposit{value: 1 ether}("ref");

        // After 1 day, deposits work again
        vm.warp(block.timestamp + 1 days);
        vm.prank(victim);
        pool.deposit{value: 1 ether}("ref"); // succeeds
    }
}
``` [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L72-94)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L244-248)
```text
    /// @notice Gets the current day relative to the start timestamp
    /// @return uint256 The current day relative to the start timestamp
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```
