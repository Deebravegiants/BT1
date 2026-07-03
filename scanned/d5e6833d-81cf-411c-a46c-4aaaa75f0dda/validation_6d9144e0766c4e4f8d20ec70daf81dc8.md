### Title
Stale Chainlink Price in `instantWithdrawal` Allows Over-Redemption from `LRTUnstakingVault` — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` discards the `updatedAt` return value from `latestRoundData`, performing no staleness check. `instantWithdrawal` uses this live-but-potentially-stale price as the denominator in `getExpectedAssetAmount`, with no price-bounds guard (unlike `unlockQueue`, which enforces caller-supplied min/max bounds). A stale, deflated asset price inflates `assetAmountUnlocked`, letting an attacker burn a small amount of rsETH and redeem a disproportionately large amount of yield-bearing assets from `LRTUnstakingVault`.

---

### Finding Description

**Root cause 1 — no staleness check in `ChainlinkPriceOracle.getAssetPrice`:**

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 52
(, int256 price,,,) = priceFeed.latestRoundData();
```

The five return values of `latestRoundData` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is consumed; `updatedAt` and `answeredInRound` are silently dropped. There is no check of the form `if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert`. [1](#0-0) 

**Root cause 2 — `instantWithdrawal` has no price-bounds guard:**

`unlockQueue` passes caller-supplied `minimumAssetPrice` / `maximumAssetPrice` to `_validatePrices`, which reverts if the live price is outside the window: [2](#0-1) 

`instantWithdrawal` performs no equivalent check. It calls `getExpectedAssetAmount` directly and uses the result without any sanity bound: [3](#0-2) 

**The vulnerable formula:**

```
assetAmountUnlocked = rsETHUnstaked * rsETHPrice / getAssetPrice(asset)
```

`rsETHPrice` is a **stored** value updated by `updateRSETHPrice()`. `getAssetPrice(asset)` is read **live** from Chainlink at call time. If the Chainlink feed is stale and returns a deflated price, the division yields a value larger than the fair ETH equivalent of the rsETH burned. [4](#0-3) 

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield (and principal) from `LRTUnstakingVault`.**

The attacker burns rsETH worth `X` ETH but redeems assets worth `X * (fairPrice / stalePrice)` ETH. The surplus comes directly from `LRTUnstakingVault`, draining yield-bearing assets (stETH, ETHx, etc.) that belong to other protocol participants. The `instantWithdrawalFee` (0–10 %) reduces but does not eliminate the profit when the price deviation is large enough. [5](#0-4) 

---

### Likelihood Explanation

**Likelihood: Medium.**

Chainlink feeds for LST assets (stETH/ETH, ETHx/ETH) have heartbeat intervals of 1–24 hours and deviation thresholds of 0.5–1 %. A feed can go stale without any oracle operator action during network congestion, Chainlink node downtime, or a period where the price has not moved enough to trigger the deviation update. An attacker monitoring on-chain `updatedAt` values can detect staleness and act within the same block. No privileged access, front-running of admin transactions, or oracle operator compromise is required.

---

### Recommendation

1. **Add a staleness check in `ChainlinkPriceOracle.getAssetPrice`:**

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
require(price > 0, "Non-positive price");
```

2. **Add price-bounds validation to `instantWithdrawal`**, mirroring the `_validatePrices` pattern already used in `unlockQueue`. Accept caller-supplied (or governance-configured) min/max bounds for both `rsETHPrice` and `assetPrice` and revert if either is outside the window. [6](#0-5) 

---

### Proof of Concept

Fork-test outline (Foundry, mainnet fork):

```solidity
// 1. Deploy a MockAggregator that returns a price 30% below the real stETH/ETH rate
//    and an updatedAt timestamp 25 hours in the past.
MockAggregator staleFeed = new MockAggregator(
    realPrice * 70 / 100,   // deflated by 30%
    block.timestamp - 25 hours
);

// 2. As LRTManager, point the stETH price feed to the mock.
chainlinkOracle.updatePriceFeedFor(stETH, address(staleFeed));

// 3. Attacker acquires rsETHUnstaked worth fairValue ETH at the real price.
uint256 rsETHUnstaked = 1 ether;
uint256 fairAssetAmount = rsETHUnstaked * rsETHPrice / realAssetPrice;

// 4. Call instantWithdrawal — no staleness revert, no price-bounds revert.
withdrawalManager.instantWithdrawal(stETH, rsETHUnstaked, "");

// 5. Assert attacker received more than fair value.
uint256 received = stETH.balanceOf(attacker);
// received ≈ rsETHUnstaked * rsETHPrice / (realPrice * 0.70)
//           = fairAssetAmount / 0.70  ≈ fairAssetAmount * 1.43
assert(received > fairAssetAmount);
// Profit ≈ 43% of fairAssetAmount, minus instantWithdrawalFee.
```

The assertion passes on unmodified production code because `ChainlinkPriceOracle.getAssetPrice` never checks `updatedAt` and `instantWithdrawal` never validates the price against any bounds. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L228-235)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L237-238)
```text
        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;
```

**File:** contracts/LRTWithdrawalManager.sol (L268-295)
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
    {
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));

        UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);

        _validatePrices(
            params.rsETHPrice,
            params.assetPrice,
            minimumRsEthPrice,
            maximumRsEthPrice,
            minimumAssetPrice,
            maximumAssetPrice
        );
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L853-870)
```text
    function _validatePrices(
        uint256 rsETHPrice,
        uint256 assetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumRsEthPrice,
        uint256 minimumAssetPrice,
        uint256 maximumAssetPrice
    )
        internal
        pure
    {
        if (rsETHPrice < minimumRsEthPrice || rsETHPrice > maximumRsEthPrice) {
            revert RsETHPriceOutOfPriceRange(rsETHPrice);
        }
        if (assetPrice < minimumAssetPrice || assetPrice > maximumAssetPrice) {
            revert AssetPriceOutOfPriceRange(assetPrice);
        }
    }
```
