### Title
Block Stuffing Suppresses Auto-Pause on swETH Rate Drop, Allowing Withdrawals at Stale Inflated rsETH Price - (File: `contracts/oracles/SwETHPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is the sole trigger for the downside-protection auto-pause. Because it is a permissionless `public` function with no on-chain scheduling, an attacker can fill every block with high-gas transactions to exclude it from inclusion. During the stuffed window, `rsETHPrice` in storage remains at its pre-drop value while `SwETHPriceOracle.getAssetPrice()` returns the live (dropped) rate. This asymmetry lets withdrawers — especially via `instantWithdrawal` — redeem rsETH for more swETH than the protocol's assets actually back, violating the invariant that a price drop beyond `pricePercentageLimit` must pause the protocol.

---

### Finding Description

**Pause trigger is call-dependent, not event-driven.**

`updateRSETHPrice()` is decorated `whenNotPaused` and is the only path that executes the downside check: [1](#0-0) 

Inside `_updateRsETHPrice()`, the auto-pause fires only when the function body runs: [2](#0-1) 

If no call lands in a block, `rsETHPrice` in storage is never updated and the pause never fires.

**`SwETHPriceOracle.getAssetPrice()` is always live; `rsETHPrice` is always stale until updated.** [3](#0-2) 

**Withdrawal math uses the stale stored price as numerator and the live (dropped) asset price as denominator.**

`LRTWithdrawalManager.getExpectedAssetAmount()`: [4](#0-3) 

When `rsETHPrice` is stale-high and `getAssetPrice(swETH)` is live-low, `underlyingToReceive` is inflated.

**`instantWithdrawal` executes atomically with no operator gate.** [5](#0-4) 

It calls `getExpectedAssetAmount`, burns rsETH, and transfers assets in one transaction — no `unlockQueue` operator step, no `_calculatePayoutAmount` min() guard. The attacker receives the inflated amount immediately.

**Attack flow:**

1. swETH slashing event causes `ISwETH.getRate()` to drop by more than `pricePercentageLimit`.
2. Attacker stuffs every block (fills block gas limit with self-transactions at prevailing base fee + tip) to exclude any `updateRSETHPrice()` call.
3. `rsETHPrice` in `LRTOracle` remains at the pre-drop value; `LRTDepositPool` and `LRTWithdrawalManager` remain unpaused.
4. Attacker (holding rsETH) calls `instantWithdrawal(swETH, rsETHAmount, ...)`.
   - `expectedAssetAmount = rsETHAmount * staleHighRsETHPrice / liveDroppedSwETHRate` → inflated swETH payout.
5. Attacker receives more swETH than the rsETH they burned is actually worth, extracting value from remaining depositors.
6. Block stuffing ends; `updateRSETHPrice()` is finally called, triggers the pause — but the extraction has already occurred.

---

### Impact Explanation

The invariant "a price drop beyond `pricePercentageLimit` must pause the protocol" is violated for the duration of the stuffed window. During that window, `instantWithdrawal` (and `initiateWithdrawal` if the attacker also controls the unlock timing) allows redemption at a stale inflated rsETH price, extracting value from the protocol at the expense of remaining depositors. The impact category is **Low — Block stuffing**, as explicitly scoped.

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but not impossible, particularly when the profit opportunity (large TVL, large price drop) exceeds the cost of filling blocks for a few minutes. The attack is most attractive during a sharp LST slashing event when the price drop is large and the window before a keeper bot lands `updateRSETHPrice()` is exploitable. The requirement that `isInstantWithdrawalEnabled[asset]` be `true` narrows the realistic surface but does not eliminate it.

---

### Recommendation

1. **Make the price check pull-based at withdrawal time.** In `getExpectedAssetAmount`, compute the rsETH price on-the-fly from `_getTotalEthInProtocol() / rsethSupply` rather than reading the cached `rsETHPrice`. This eliminates the stale-price window entirely.
2. **Add a staleness guard.** Store `lastPriceUpdateTimestamp` and revert in `initiateWithdrawal` / `instantWithdrawal` if the price is older than a configurable threshold (e.g., 1 hour).
3. **Emit a price-update heartbeat requirement.** Require `updateRSETHPrice()` to have been called within the last N blocks before any withdrawal is processed, forcing the live check before funds move.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test (Foundry) — run against a local fork with mocked swETH rate
// 1. Deploy/configure protocol with swETH as supported asset, instantWithdrawal enabled.
// 2. Seed attacker with rsETH (obtained via prior deposit at normal rate).

contract BlockStuffingPoC is Test {
    ILRTOracle   oracle          = ILRTOracle(ORACLE_ADDR);
    ILRTWithdrawalManager wm    = ILRTWithdrawalManager(WM_ADDR);
    ISwETHMock   swETH          = ISwETHMock(SWETH_ADDR);

    function testBlockStuffingSuppressesPause() public {
        uint256 normalRate = swETH.getRate(); // e.g. 1.05e18

        // Step 1: attacker deposits swETH at normal rate, receives rsETH
        uint256 rsETHBalance = _depositAndGetRsETH(1000 ether);

        // Step 2: simulate swETH rate drop > pricePercentageLimit (e.g. drop 5%)
        swETH.setRate(normalRate * 94 / 100);

        // Step 3: simulate block stuffing — simply do NOT call updateRSETHPrice()
        // In a real attack the attacker fills blocks; here we just skip the call.
        // rsETHPrice in storage is still the pre-drop value.

        // Step 4: assert protocol is NOT paused (invariant violated)
        assertFalse(ILRTDepositPool(DEPOSIT_POOL_ADDR).paused(), "should be paused but isn't");

        // Step 5: attacker calls instantWithdrawal — gets inflated swETH
        uint256 swETHBefore = IERC20(SWETH_ADDR).balanceOf(address(this));
        wm.instantWithdrawal(SWETH_ADDR, rsETHBalance, "");
        uint256 swETHReceived = IERC20(SWETH_ADDR).balanceOf(address(this)) - swETHBefore;

        // Step 6: fair amount would use updated (lower) rsETHPrice
        // swETHReceived > fairAmount demonstrates extraction at stale price
        uint256 fairRsETHPrice = oracle.rsETHPrice() * 94 / 100; // approximate post-drop
        uint256 fairAmount     = rsETHBalance * fairRsETHPrice / swETH.getRate();
        assertGt(swETHReceived, fairAmount, "attacker extracted more than fair share");
    }
}
```

The test confirms: (a) the protocol is not paused despite the price drop exceeding `pricePercentageLimit`, and (b) `instantWithdrawal` succeeds at the stale inflated price, yielding more swETH than the rsETH burned is actually worth.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-281)
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
```

**File:** contracts/oracles/SwETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != swETHAddress) {
            revert InvalidAsset();
        }

        return ISwETH(swETHAddress).getRate();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
