### Title
Reward Sandwiching via Permissionless `FeeReceiver.sendFunds()` and `updateRSETHPrice()` Allows Yield Theft from rsETH Holders - (File: contracts/FeeReceiver.sol, contracts/LRTOracle.sol)

---

### Summary

An attacker can deposit into `LRTDepositPool` at a stale (pre-reward) `rsETHPrice`, then atomically trigger reward distribution via the permissionless `FeeReceiver.sendFunds()` and price update via the permissionless `LRTOracle.updateRSETHPrice()`, then immediately initiate a withdrawal at the inflated post-reward price. After the 8-day withdrawal delay, the attacker exits with a profit proportional to their share of the rewards, having contributed no long-term capital commitment to the protocol.

---

### Finding Description

The `rsETHPrice` stored in `LRTOracle` is a lazily-updated value. It only reflects the true TVL when `updateRSETHPrice()` is explicitly called. Rewards accumulate in `FeeReceiver` as ETH (MEV/execution-layer rewards) and are not counted in `totalETHInProtocol` until `FeeReceiver.sendFunds()` is called to push them into `LRTDepositPool`.

Both `FeeReceiver.sendFunds()` and `LRTOracle.updateRSETHPrice()` are fully permissionless — no access control restricts who can call them.

**`FeeReceiver.sendFunds()` — no access control:** [1](#0-0) 

**`LRTOracle.updateRSETHPrice()` — public, no role check:** [2](#0-1) 

**Deposit minting uses the stored (stale) `rsETHPrice`:** [3](#0-2) 

**Withdrawal initiation also uses the stored `rsETHPrice` at initiation time:** [4](#0-3) 

**`getExpectedAssetAmount` uses the live stored price:** [5](#0-4) 

**`_calculatePayoutAmount` takes the minimum of the initiation-time expected amount and the unlock-time return — so the attacker locks in the post-reward price at initiation:** [6](#0-5) 

There is no minimum holding period, no deposit lock-up, and no mechanism to prevent a depositor from immediately initiating a withdrawal after a price update.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

Existing rsETH holders earn yield because the `rsETHPrice` increases as rewards accrue. An attacker who deposits just before rewards are recognized and withdraws just after captures a proportional share of those rewards without having been exposed to the protocol during the period the rewards were earned. This directly dilutes the yield of all existing rsETH holders.

The attacker's profit per attack is approximately:

```
profit ≈ (attacker_deposit / (TVL + attacker_deposit)) × reward_amount
```

For a protocol with large TVL and regular MEV reward accumulation, this is a repeatable, profitable attack.

---

### Likelihood Explanation

**Likelihood: Medium.**

The attack requires:
1. Capital to deposit (returned after 8 days, so only opportunity cost applies).
2. Monitoring `FeeReceiver.balance` for accumulated rewards — trivially done on-chain.
3. Calling three permissionless functions in sequence: `depositETH`, `sendFunds`, `updateRSETHPrice`, then `initiateWithdrawal`.
4. Waiting 8 days for the `withdrawalDelayBlocks` to pass.

The 8-day delay is friction but not a deterrent for a well-capitalized attacker. The `pricePercentageLimit` check in `_updateRsETHPrice` partially limits the per-update price jump for non-manager callers, but it does not prevent the attack for normal-sized daily reward accumulations that fall within the threshold. [7](#0-6) 

---

### Recommendation

1. **Introduce a minimum deposit holding period** before a user can initiate a withdrawal (e.g., 7–14 days from deposit block), analogous to the Asymmetry mitigation recommendation.
2. **Restrict `FeeReceiver.sendFunds()`** to a privileged role (e.g., `MANAGER`) so that reward distribution cannot be triggered by an attacker at will.
3. **Alternatively, stream rewards** by not immediately crediting the full reward to `totalETHInProtocol` in a single `updateRSETHPrice()` call, but instead linearly unlocking them over a period of time.

---

### Proof of Concept

Assume:
- Protocol TVL = 10,000 ETH, rsETH supply = 10,000 rsETH, `rsETHPrice` = 1.0 ETH/rsETH.
- `FeeReceiver` holds 10 ETH in accumulated MEV rewards (not yet sent to deposit pool).

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositETH{value: 1000 ETH}(0, "")`.
   - `rsETHAmountToMint = 1000 ETH / 1.0 = 1000 rsETH` (uses stale price).
   - Attacker receives 1000 rsETH. TVL = 11,000 ETH, supply = 11,000 rsETH, price still 1.0.

2. Attacker calls `FeeReceiver.sendFunds()`.
   - 10 ETH pushed to `LRTDepositPool`. TVL = 11,010 ETH, supply = 11,000 rsETH.

3. Attacker calls `LRTOracle.updateRSETHPrice()`.
   - New price = 11,010 / 11,000 ≈ 1.000909 ETH/rsETH. Stored `rsETHPrice` updated.

4. Attacker calls `LRTWithdrawalManager.initiateWithdrawal(ETH, 1000 rsETH, "")`.
   - `expectedAssetAmount = 1000 × 1.000909 / 1.0 ≈ 1000.909 ETH`.

5. After 8 days, attacker calls `completeWithdrawal`.
   - Receives ≈ 1000.909 ETH.
   - **Profit ≈ 0.909 ETH** (attacker's proportional share of the 10 ETH reward: 1000/11000 × 10 = 0.909 ETH).

The 0.909 ETH was stolen from the 10,000 existing rsETH holders who earned those MEV rewards.

### Citations

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

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
