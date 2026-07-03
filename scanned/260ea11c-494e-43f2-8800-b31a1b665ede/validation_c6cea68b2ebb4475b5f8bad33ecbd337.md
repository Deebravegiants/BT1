### Title
Deposit-Before-Price-Update Arbitrage via Public `updateRSETHPrice()` and `instantWithdrawal()` - (File: contracts/LRTOracle.sol, contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a permissionless public function. An attacker can atomically: (1) deposit ETH/LST at the current stale (lower) `rsETHPrice`, (2) call `updateRSETHPrice()` to push the price up to reflect accrued rewards, and (3) call `LRTWithdrawalManager.instantWithdrawal()` at the newly elevated price — extracting more assets than deposited and stealing yield from all other rsETH holders.

---

### Finding Description

`LRTOracle.rsETHPrice` is a stored value updated only when `updateRSETHPrice()` is explicitly called. Between updates, rewards accrue in EigenLayer, causing the true backing per rsETH to exceed the stored price. Because `updateRSETHPrice()` is unrestricted (`public whenNotPaused`), any caller can trigger it at will.

The deposit path in `LRTDepositPool` mints rsETH using the **current stored** `rsETHPrice`:

```solidity
// LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

A lower `rsETHPrice` yields **more** rsETH for the same deposit amount.

The instant-withdrawal path in `LRTWithdrawalManager` redeems assets using the **current stored** `rsETHPrice` at withdrawal time:

```solidity
// LRTWithdrawalManager.sol:593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

A higher `rsETHPrice` yields **more** assets for the same rsETH amount.

The attacker exploits the gap between these two moments:

1. **Deposit** at stale low `rsETHPrice` → receive inflated rsETH amount.
2. **Call `updateRSETHPrice()`** → price rises to reflect accrued rewards.
3. **Call `instantWithdrawal()`** → redeem rsETH at the elevated price, receiving more assets than deposited.

All three steps can be executed atomically in a single transaction.

`instantWithdrawal()` does correctly burn rsETH:

```solidity
// LRTWithdrawalManager.sol:229
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

However, the burn does not prevent the arbitrage — it only prevents the double-spend of the token itself. The profit comes from the price delta between deposit and withdrawal, not from unburned tokens.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

Concretely: if `rsETHPrice` is stale at `1.00e18` and the true price after rewards is `1.01e18`, an attacker depositing `100 ETH` receives `100 rsETH` (at the stale price). After calling `updateRSETHPrice()`, they instantly withdraw `100 rsETH` for `101 ETH` (at the updated price), netting `1 ETH` profit minus the `instantWithdrawalFee`. This profit is extracted directly from the yield that should have been distributed pro-rata to all existing rsETH holders, reducing the effective `rsETHPrice` increase they receive.

The `instantWithdrawalFee` (capped at 10% by `setInstantWithdrawalFee`) can reduce but not eliminate the profit if the fee is set below the reward accrual rate. The `pricePercentageLimit` bounds the per-update price increase but does not prevent repeated attacks across multiple update cycles.

---

### Likelihood Explanation

**Likelihood: Medium.**

Prerequisites that must hold simultaneously:
- `isInstantWithdrawalEnabled[asset]` must be `true` (operator-controlled flag).
- `LRTUnstakingVault` must hold sufficient assets for instant withdrawal (normal operational state when unstaking is active).
- `rsETHPrice` must be stale (rewards have accrued since the last `updateRSETHPrice()` call — this is the normal state between oracle updates).
- `instantWithdrawalFee` must be less than the pending reward accrual percentage.

All conditions are routinely satisfied during normal protocol operation when instant withdrawals are enabled. The attack requires no privileged access and is fully atomic.

---

### Recommendation

1. **Update `rsETHPrice` atomically inside `depositETH`/`depositAsset`** before computing the rsETH mint amount, so deposits always use the freshest price.
2. **Alternatively**, record the `rsETHPrice` at deposit time and use the **minimum** of the deposit-time price and the withdrawal-time price when computing `instantWithdrawal` payouts — analogous to how `_calculatePayoutAmount` already applies a min-of-two-prices logic for queued withdrawals.
3. **Ensure `instantWithdrawalFee` is set high enough** to exceed the maximum possible single-update reward accrual rate as a defense-in-depth measure.

---

### Proof of Concept

```solidity
// Attacker contract — executes atomically in one transaction
function attack(
    ILRTDepositPool depositPool,
    ILRTOracle oracle,
    ILRTWithdrawalManager withdrawalManager,
    uint256 depositAmount
) external payable {
    // Step 1: Deposit at stale (low) rsETHPrice
    depositPool.depositETH{value: depositAmount}(0, "arb");

    // Step 2: Trigger price update — rsETHPrice rises to reflect accrued rewards
    oracle.updateRSETHPrice();

    // Step 3: Instantly withdraw at the new (higher) rsETHPrice
    uint256 rsETHBalance = IERC20(rsETHToken).balanceOf(address(this));
    withdrawalManager.instantWithdrawal(ETH_TOKEN, rsETHBalance, "arb");

    // address(this).balance > depositAmount — profit extracted from other holders
}
```

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-313)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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
        }

        // downside protection — pause if price drops too far
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

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
