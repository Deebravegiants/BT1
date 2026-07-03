### Title
Multi-Asset Deposit/Withdrawal Allows Socializing LST Slashing Losses onto rsETH Holders - (`contracts/LRTWithdrawalManager.sol` / `contracts/LRTDepositPool.sol`)

---

### Summary

The LRT-rsETH protocol accepts multiple LST assets (stETH, ETHx, ETH) and allows users to deposit one asset and withdraw a *different* asset. Because rsETH's price is a basket-weighted average, a predictable drop in one LST causes the rsETH price to fall by only a fraction of the individual asset's drop. An attacker who deposits the depreciating LST before the drop and withdraws a different asset (e.g., ETH) after the drop receives more ETH than their LST is currently worth, transferring part of their loss to other rsETH holders.

---

### Finding Description

**Deposit path** — `LRTDepositPool.depositAsset()` accepts any supported LST and mints rsETH using:

```
rsethAmountToMint = (amount × assetPrice) / rsETHPrice
``` [1](#0-0) 

**Withdrawal path** — `LRTWithdrawalManager.initiateWithdrawal()` accepts *any* supported asset as the withdrawal target, completely independent of what was deposited:

```
expectedAssetAmount = rsETHUnstaked × rsETHPrice / assetPrice
``` [2](#0-1) [3](#0-2) 

**Payout cap** — `_calculatePayoutAmount` applies `min(expectedAssetAmount, currentReturn)` at unlock time:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [4](#0-3) 

This cap reduces but **does not eliminate** the impact. When the attacker withdraws ETH (whose price is always 1.0 ETH), `currentReturn` equals `rsETHUnstaked × P_rsETH_after`. The rsETH price drops proportionally to the LST's *weight* in the basket — less than the individual LST price drop — so the attacker still recovers more ETH than their LST is currently worth.

**rsETH price is a basket average** computed in `_getTotalEthInProtocol()`:

```solidity
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [5](#0-4) 

If stETH is weight `w` of the basket and drops by `d`, rsETH price drops by only `w × d`. The attacker recovers `amount × P_stETH_before × (1 − w×d)` in ETH, while their stETH is worth `amount × P_stETH_before × (1 − d)`. The difference — `amount × P_stETH_before × d × (1 − w)` — is borne by other rsETH holders.

**Instant withdrawal path** — `instantWithdrawal()` has no delay and uses the same `getExpectedAssetAmount()` formula, making the attack executable immediately after the price drop if enabled: [6](#0-5) 

---

### Impact Explanation

**Medium.** The attacker transfers a portion of their LST slashing loss to other rsETH holders. The transferred amount is `deposit_value × drop_rate × (1 − LST_basket_weight)`. For a 10% stETH drop with stETH at 50% of the basket, the attacker transfers 5% of their deposit value to other rsETH holders. This is a direct, quantifiable loss of funds for existing rsETH holders — matching the "contract fails to deliver promised returns" / "temporary fund loss" impact class.

---

### Likelihood Explanation

**Low-Medium.** The attack requires:
1. Predicting an LST price drop in advance — feasible for slashing events (which unfold over days/weeks) or large queued withdrawals from liquid staking providers.
2. Holding the depreciating LST in sufficient size.
3. For the standard path: tolerating the 8-day `withdrawalDelayBlocks` window.
4. For `instantWithdrawal`: the manager must have enabled it for the target asset.

The `pricePercentageLimit` in `LRTOracle` pauses the protocol on large drops, but smaller drops (within the limit) remain exploitable. [7](#0-6) 

---

### Recommendation

1. **Restrict withdrawal asset to deposited asset** — track which asset each user deposited and only allow withdrawal of that same asset.
2. **Minimum deposit-to-withdrawal period** — enforce a lock-up period longer than the maximum predictable slashing window.
3. **Deposit freeze on oracle price anomalies** — pause new deposits when a supported LST's oracle price drops significantly within a short window.
4. **Per-asset withdrawal queues** — already partially implemented; ensure the `assetsCommitted` accounting prevents cross-asset arbitrage.

---

### Proof of Concept

**Setup**: Protocol holds 100 ETH + 100 stETH (at 1.05 ETH/stETH). Total TVL = 205 ETH. rsETH supply = 205. rsETH price = 1.0 ETH.

**Step 1 — Attacker deposits 100 stETH** (worth 105 ETH):
- `rsETH minted = (100 × 1.05) / 1.0 = 105 rsETH`
- New TVL = 310 ETH, rsETH supply = 310, rsETH price = 1.0 ETH

**Step 2 — Attacker calls `initiateWithdrawal(ETH, 105)`**:
- `expectedAssetAmount = 105 × 1.0 / 1.0 = 105 ETH` (locked in)

**Step 3 — stETH drops 10%** → stETH price = 0.945 ETH:
- New TVL = 100 + 200 × 0.945 = 289 ETH
- `updateRSETHPrice()` → rsETH price = 289 / 310 ≈ 0.9323 ETH

**Step 4 — After 8 days, operator calls `unlockQueue(ETH, ...)`**:
- `currentReturn = 105 × 0.9323 / 1.0 ≈ 97.89 ETH`
- `payout = min(105, 97.89) = 97.89 ETH`

**Result**:
- Attacker receives **97.89 ETH**
- Attacker's 100 stETH is worth **94.5 ETH** (100 × 0.945)
- **Attacker profit: ~3.39 ETH** transferred from other rsETH holders
- Original 205 rsETH holders hold 191.1 ETH instead of 194.5 ETH — a **3.4 ETH loss** they did not cause [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
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
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
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

**File:** contracts/LRTWithdrawalManager.sol (L770-816)
```text
    function _unlockWithdrawalRequests(
        address asset,
        uint256 availableAssetAmount,
        uint256 rsETHPrice,
        uint256 assetPrice,
        uint256 firstExcludedIndex
    )
        internal
        returns (uint256 rsETHAmountToBurn, uint256 assetAmountToUnlock)
    {
        // Check that upper limit is in the range of existing withdrawal requests. If it is greater set it to the first
        // nonce with no withdrawal request.
        if (firstExcludedIndex > nextUnusedNonce[asset]) {
            firstExcludedIndex = nextUnusedNonce[asset];
        }

        uint256 nextLockedNonce_ = nextLockedNonce[asset];
        // Revert when trying to unlock a request that has already been unlocked
        if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();

        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
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

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```
