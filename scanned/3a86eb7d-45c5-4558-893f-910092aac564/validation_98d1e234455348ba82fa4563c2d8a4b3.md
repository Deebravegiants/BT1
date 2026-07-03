### Title
Unprivileged Caller Can Atomically Pause Three Contracts via `updateRSETHPrice()` Downside Protection — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public function with no access-control guard. Its internal downside-protection logic calls `pause()` on `LRTDepositPool`, `LRTWithdrawalManager`, and itself in a single transaction whenever the computed price drops more than `pricePercentageLimit` below `highestRsethPrice`. Any unprivileged EOA can invoke this path whenever oracle prices reflect a sufficient drop, temporarily freezing all user-facing operations across three contracts until three separate admin `unpause()` calls are made.

---

### Finding Description

**Entry point — no access control:**

`updateRSETHPrice()` is declared `public` with only the `whenNotPaused` modifier: [1](#0-0) 

No role check exists. Any EOA or contract can call it at any time the oracle is not already paused.

**Downside-protection branch — atomic three-contract pause:**

Inside `_updateRsETHPrice()`, when `newRsETHPrice < highestRsethPrice` and the absolute difference exceeds `pricePercentageLimit × highestRsethPrice`: [2](#0-1) 

All three contracts are paused in one transaction and the function returns immediately, skipping the price update.

**`IPausable` is a local minimal interface:** [3](#0-2) 

For these cross-contract `pause()` calls to succeed, `LRTOracle` must hold `PAUSER_ROLE` on both `LRTDepositPool` and `LRTWithdrawalManager` — a prerequisite for the downside-protection feature to function at all, so it must be true in any correct deployment.

**Downstream impact — all user operations blocked:**

- `LRTWithdrawalManager.completeWithdrawal()` — `whenNotPaused` [4](#0-3) 
- `LRTWithdrawalManager.initiateWithdrawal()` — `whenNotPaused` [5](#0-4) 
- `LRTWithdrawalManager.unlockQueue()` — `whenNotPaused` [6](#0-5) 
- `LRTDepositPool.depositETH()` / `depositAsset()` — `whenNotPaused` [7](#0-6) 

**Recovery requires three separate privileged transactions:**

- `LRTOracle.unpause()` — `onlyLRTAdmin` [8](#0-7) 
- `LRTWithdrawalManager.unpause()` — `onlyLRTAdmin` [9](#0-8) 
- `LRTDepositPool.unpause()` — requires admin role as well [10](#0-9) 

**The threshold is relative to the all-time high, not the current price:**

`highestRsethPrice` is the historical peak, never decremented: [11](#0-10) 

This means even a stable, slowly-appreciating protocol can be frozen if the current price is more than `pricePercentageLimit` below a historical spike — a condition that can persist for extended periods without any oracle manipulation.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Users with rsETH already locked in `initiateWithdrawal` queues cannot call `completeWithdrawal`. Operators cannot call `unlockQueue`. New deposits are blocked. All three contracts remain frozen until three separate admin unpause transactions are confirmed on-chain. Funds are not lost, but access is denied for the duration.

---

### Likelihood Explanation

The trigger requires only that the oracle-reported rsETH price be more than `pricePercentageLimit` below `highestRsethPrice` at the moment the attacker calls `updateRSETHPrice()`. This condition arises naturally from:

- Any LST experiencing a temporary depeg or market dip
- A historical price spike that set `highestRsethPrice` high, followed by a modest correction
- A low `pricePercentageLimit` setting (e.g., 2 %, i.e., `2e16`)

No oracle manipulation, private key compromise, or governance capture is required. The attacker monitors oracle prices off-chain and calls the public function at the opportune moment.

---

### Recommendation

1. **Add access control to `updateRSETHPrice()`** — restrict it to `MANAGER` or a dedicated `PRICE_UPDATER` role, or at minimum emit a warning event and require a keeper role for the pause-triggering path.
2. **Separate the pause trigger from the price-update path** — the downside-protection pause should be callable only by a privileged role, not as a side-effect of a public price update.
3. **Use a rolling window or moving average** for `highestRsethPrice` rather than an all-time high, to reduce the attack surface from historical price spikes.
4. **Implement a single `unpauseAll()` admin function** in `LRTConfig` to reduce recovery friction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Setup (local fork / unit test):
// 1. Deploy LRTConfig, LRTOracle, LRTDepositPool, LRTWithdrawalManager with standard init.
// 2. Grant LRTOracle PAUSER_ROLE on LRTDepositPool and LRTWithdrawalManager
//    (required for downside protection to function).
// 3. Admin calls: lrtOracle.setPricePercentageLimit(2e16); // 2%
// 4. Seed protocol: user deposits stETH, receives rsETH, calls initiateWithdrawal.
// 5. Advance oracle so rsETHPrice reaches 1.05 ether → highestRsethPrice = 1.05 ether.
// 6. Drop mock asset oracle price by 3% so new computed rsETHPrice ≈ 1.0185 ether
//    (> 2% below highestRsethPrice of 1.05 ether).
// 7. Attacker (unprivileged EOA) calls:
//      lrtOracle.updateRSETHPrice();
// 8. Assert:
//      assertTrue(lrtOracle.paused());
//      assertTrue(lrtDepositPool.paused());
//      assertTrue(lrtWithdrawalManager.paused());
// 9. User calls completeWithdrawal → reverts with ContractPaused / EnforcedPause.
// 10. Count admin txs to restore: unpause LRTOracle + unpause LRTDepositPool
//     + unpause LRTWithdrawalManager = 3 separate privileged transactions.
```

### Citations

**File:** contracts/LRTOracle.sol (L16-19)
```text
interface IPausable {
    function pause() external;
    function paused() external view returns (bool);
}
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L292-296)
```text

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-161)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
```

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L268-281)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L352-354)
```text
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

**File:** contracts/LRTDepositPool.sol (L80-84)
```text
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
```

**File:** contracts/LRTConfig.sol (L262-270)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
```
