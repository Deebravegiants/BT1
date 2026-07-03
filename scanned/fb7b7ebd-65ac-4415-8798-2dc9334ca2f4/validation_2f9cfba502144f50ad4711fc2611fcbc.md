Now I have all the information needed to analyze this fully. Let me trace the complete attack path.

### Title
Unguarded Near-Zero Chainlink Price Commits Corrupted `rsETHPrice` When `pricePercentageLimit == 0`, Enabling Mint-at-Near-Zero-Price Attack — (`contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` has no runtime minimum price floor. When `pricePercentageLimit == 0` (the default, unset state), `LRTOracle._updateRsETHPrice()` has no downside circuit-breaker either. A Chainlink feed that transiently returns a near-zero answer (depegging event, feed misconfiguration) causes `rsETHPrice` to be committed as near-zero. Once the feed recovers, any depositor can call `depositAsset()` and receive a massively disproportionate rsETH mint, diluting all existing holders.

---

### Finding Description

**`ChainlinkPriceOracle.getAssetPrice()` — no runtime price floor** [1](#0-0) 

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No staleness check, no negative-price check, no minimum floor. `price = 1` with `decimals = 8` returns `1e10` (0.00000001 ETH), which passes silently.

Note: `updatePriceOracleForValidated` does enforce `price ∈ [1e16, 1e19]` at oracle-setup time, but this is a one-time check that does not protect against runtime price drift. [2](#0-1) 

**`LRTOracle._updateRsETHPrice()` — downside circuit-breaker is gated on `pricePercentageLimit > 0`** [3](#0-2) 

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

if (isPriceDecreaseOffLimit) {
    ...pause...
    return;   // rsETHPrice is NOT written
}
```

`pricePercentageLimit` is **never set in `initialize()`** — it defaults to `0`. When it is `0`, `isPriceDecreaseOffLimit` is always `false` regardless of how catastrophic the price drop is. Execution falls through to line 313: [4](#0-3) 

```solidity
rsETHPrice = newRsETHPrice;   // near-zero price committed
```

No pause is triggered, no early return, and the corrupted price is stored.

**`LRTDepositPool.getRsETHAmountToMint()` — uses live asset price over stale `rsETHPrice`** [5](#0-4) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.rsETHPrice()` is the **stored** value (updated only on `updateRSETHPrice()` calls). `lrtOracle.getAssetPrice(asset)` reads the **live** Chainlink price. Once the feed recovers, the numerator is normal (~1e18) while the denominator is near-zero (~1e10), yielding a ~1e8× inflation of minted rsETH.

---

### Impact Explanation

Existing rsETH holders are diluted. An attacker depositing 1 LST (1e18 wei) when `rsETHPrice = 1e10` and `getAssetPrice = 1e18` receives:

```
rsethAmountToMint = (1e18 * 1e18) / 1e10 = 1e26 rsETH
```

against a total existing supply that might be ~1e24. The attacker then holds the overwhelming majority of rsETH supply and can redeem it for the protocol's real collateral, constituting direct theft from all existing holders. This is **Critical — Protocol Insolvency / Direct Theft of User Funds**.

The `RSETH.checkDailyMintLimit` modifier caps total daily mints, but `maxMintAmountPerDay` must be set to a large value for normal protocol operation, so it limits but does not prevent the attack. [6](#0-5) 

---

### Likelihood Explanation

- `pricePercentageLimit == 0` is the **default state** after `initialize()`. No admin action is needed to be in the vulnerable state; an admin action is required to escape it.
- `updateRSETHPrice()` is a **public, permissionless function** — anyone can call it during a bad-price window.
- LST depegging events (stETH, rETH, etc.) and Chainlink feed misconfiguration are historically documented real-world occurrences.
- The attacker does not need to control the feed; they only need to observe the bad-price window and act opportunistically.

---

### Recommendation

1. **Add a runtime minimum price floor in `ChainlinkPriceOracle.getAssetPrice()`**: revert if `price <= 0` or if the normalized price falls below a configurable minimum (e.g., `1e16`).
2. **Enforce `pricePercentageLimit > 0` at initialization**, or add a hard-coded minimum price drop guard in `_updateRsETHPrice()` that does not depend on `pricePercentageLimit` being set.
3. **Add a minimum `newRsETHPrice` sanity check** before committing it (e.g., revert or pause if `newRsETHPrice < rsETHPrice / 2`).

---

### Proof of Concept

```solidity
// Local fork / unit test — unmodified production contracts
// Setup: pricePercentageLimit == 0 (default, never set)
//        maxMintAmountPerDay set to a large value (required for normal operation)
//        1000 stETH deposited by existing users, rsETHPrice ~ 1e18

// 1. Set mock Chainlink feed to return answer = 1 (decimals = 8)
mockFeed.setAnswer(1);

// 2. Anyone calls the public updateRSETHPrice()
//    _getTotalEthInProtocol() returns ~1e10 (1000 * 1e18 * 1e10 / 1e18)
//    newRsETHPrice = ~1e10 / rsethSupply ≈ near-zero
//    pricePercentageLimit == 0 → isPriceDecreaseOffLimit = false → no pause
//    rsETHPrice = near-zero  ← committed
lrtOracle.updateRSETHPrice();

// 3. Feed recovers to normal
mockFeed.setAnswer(1e8); // 1.0 ETH per stETH (8 decimals)

// 4. Attacker deposits 1 wei of stETH
//    getAssetPrice(stETH) = 1e18 (live, recovered)
//    rsETHPrice = 1e10 (stale, near-zero)
//    rsethAmountToMint = (1 * 1e18) / 1e10 = 1e8 rsETH per wei deposited
stETH.approve(address(depositPool), 1);
depositPool.depositAsset(stETH, 1, 0, "");

// 5. Assert attacker holds disproportionate rsETH
assertGt(rsETH.balanceOf(attacker), rsETH.totalSupply() / 2);
``` [7](#0-6) [8](#0-7) [9](#0-8) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L102-107)
```text
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
