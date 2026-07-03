### Title
Stale `rsETHPrice` Exploitable via Public `updateRSETHPrice()` to Extract Value from Existing rsETH Holders - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a stored state variable that can become stale between updates. Because `updateRSETHPrice()` is publicly callable with no access control and `ChainlinkPriceOracle.getAssetPrice()` performs no staleness validation, an attacker can exploit the gap between the stale stored `rsETHPrice` and the current real-time Chainlink asset prices: deposit at the stale (lower) rate, trigger a price update, then withdraw at the new (higher) rate for a risk-free profit — directly analogous to the two-price oracle attack in the external report.

---

### Finding Description

**Root cause 1 — `ChainlinkPriceOracle.getAssetPrice()` has no staleness validation:** [1](#0-0) 

The function calls `latestRoundData()` but silently discards `updatedAt` and `answeredInRound`, accepting any price regardless of age. Compare this to `ChainlinkOracleForRSETHPoolCollateral`, which is used in the L2 pools and explicitly checks both: [2](#0-1) 

The inconsistency means the L1 oracle path is unprotected while the L2 pool oracle path is protected.

**Root cause 2 — `updateRSETHPrice()` is publicly callable:** [3](#0-2) 

Any address can trigger a price update at any time. The stored `rsETHPrice` is therefore a lagging snapshot of the protocol's true NAV.

**Root cause 3 — `getRsETHAmountToMint()` mixes a real-time Chainlink price with the stale stored price:** [4](#0-3) 

`lrtOracle.getAssetPrice(asset)` reads the current Chainlink price in real time, while `lrtOracle.rsETHPrice()` reads the stored state variable. When Chainlink prices for LST assets have risen since the last `updateRSETHPrice()` call, the denominator (`rsETHPrice`) is stale-low, so the depositor receives more rsETH than the protocol's current NAV justifies.

**Root cause 4 — `instantWithdrawal()` reads the current oracle price at execution time:** [5](#0-4) 

`getExpectedAssetAmount()` is evaluated at the moment of the call, so after the attacker triggers `updateRSETHPrice()` the withdrawal is priced at the new, higher rate.

**Attack flow (single transaction when `instantWithdrawal` is enabled):**

1. Observe that `rsETHPrice` is stale-low (Chainlink LST prices have risen since the last update).
2. Call `LRTDepositPool.depositETH()` — receives `amount / rsETHPrice_stale` rsETH (more than fair value).
3. Call `LRTOracle.updateRSETHPrice()` — stored price rises to `rsETHPrice_new`.
4. Call `LRTWithdrawalManager.instantWithdrawal()` — receives `rsETHAmount × rsETHPrice_new` ETH.

Even without `instantWithdrawal`, the same profit is locked in via `initiateWithdrawal()` immediately after step 3, because `expectedAssetAmount` is set using the freshly updated price and is paid out in full after the delay.

---

### Impact Explanation

**High — Theft of unclaimed yield.** The attacker extracts ETH that represents accrued yield belonging to existing rsETH holders. The profit is proportional to the price gap: a 1% stale gap on a 1 000 ETH deposit yields ≈ 9.5 ETH of risk-free profit, taken directly from the pool's NAV and therefore from all existing holders.

---

### Likelihood Explanation

**Medium.** The `rsETHPrice` is naturally stale between keeper calls to `updateRSETHPrice()`. Chainlink LST/ETH feeds update on a heartbeat (typically 24 h) or a 0.5% deviation threshold. Any period where the feeds have moved but `rsETHPrice` has not been refreshed opens the window. No special permissions are required; the attack is fully permissionless and can be amplified with a flash loan.

---

### Recommendation

1. **Add staleness validation to `ChainlinkPriceOracle.getAssetPrice()`** — check `answeredInRound >= roundId` and `updatedAt > block.timestamp - maxStaleness`, mirroring `ChainlinkOracleForRSETHPoolCollateral`.
2. **Restrict `updateRSETHPrice()` to trusted keepers/relayers** — remove the permissionless `public` access or add a role check, so an attacker cannot trigger a price update on demand.
3. **Use the same oracle snapshot for both deposit and withdrawal** — record the `rsETHPrice` at deposit time and cap the withdrawal payout to that snapshot, preventing the attacker from benefiting from a price update they triggered.

---

### Proof of Concept

```
State before attack:
  rsETHPrice (stored)  = 1.050e18   ← stale
  rsETHPrice (true)    = 1.060e18   ← Chainlink LST prices have risen

Step 1 — depositETH(1 000 ETH):
  rsethAmountToMint = 1000e18 * 1e18 / 1.050e18 = 952.38 rsETH
  (fair amount would be 1000e18 / 1.060e18 = 943.40 rsETH)

Step 2 — updateRSETHPrice():
  rsETHPrice (stored) → 1.060e18

Step 3 — instantWithdrawal(ETH, 952.38 rsETH):
  assetAmountUnlocked = 952.38 * 1.060e18 / 1e18 = 1 009.52 ETH

Profit = 1 009.52 - 1 000 = 9.52 ETH  (≈ 0.95%)
Source = existing rsETH holders' accrued yield
```

The attack is amplifiable with a flash loan. With 100 000 ETH the profit is ≈ 952 ETH in a single transaction.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
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
