### Title
Near-Zero Chainlink Price Bypasses Disabled Downside Protection, Enabling Mint-at-Near-Zero-Price Attack — (`contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` applies no minimum price floor. `LRTOracle._updateRsETHPrice` contains a downside-protection circuit-breaker, but it is **unconditionally disabled when `pricePercentageLimit == 0`** — the default on-chain value. When both conditions coincide (a Chainlink feed returns a near-zero price and `pricePercentageLimit` has never been set), `rsETHPrice` is written to near-zero, and any subsequent depositor of a correctly-priced asset mints rsETH at a near-zero denominator, extracting value from all existing holders.

---

### Finding Description

**Step 1 — No minimum price floor in `ChainlinkPriceOracle.getAssetPrice`** [1](#0-0) 

The function casts `price` directly to `uint256` and scales it. If the feed returns `answer = 1` with `decimals = 8`, the result is `1 * 1e18 / 1e8 = 1e10` — ten orders of magnitude below the expected ~`1e18`. No lower-bound check exists.

**Step 2 — Downside protection is gated on `pricePercentageLimit > 0`** [2](#0-1) 

The circuit-breaker evaluates:
```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```
`pricePercentageLimit` is a `uint256` storage variable with no initializer; its default value is `0`. When `pricePercentageLimit == 0`, the short-circuit makes `isPriceDecreaseOffLimit` permanently `false` regardless of how large `diff` is. The protocol never pauses, and execution falls through to line 313: [3](#0-2) 

`rsETHPrice` is overwritten with the near-zero value.

**Step 3 — `updateRSETHPrice()` is permissionlessly callable** [4](#0-3) 

Any EOA can trigger the price update.

**Step 4 — Mint ratio uses the stale near-zero `rsETHPrice`** [5](#0-4) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
If `rsETHPrice = 1e10` and the deposited asset's oracle still returns `~1e18`, the attacker receives `amount * 1e18 / 1e10 = amount * 1e8` rsETH — 100 million times the fair share.

**Registration-time check does not help at runtime**

`updatePriceOracleForValidated` validates `1e16 ≤ price ≤ 1e19` only at oracle registration time. [6](#0-5) 

It provides no protection against a price that drops after registration.

---

### Impact Explanation

An attacker who deposits a small amount of a correctly-priced LST immediately after `rsETHPrice` is set to near-zero receives rsETH representing a claim on the entire protocol TVL. When they redeem, they drain real collateral from all existing rsETH holders. This is direct theft of user funds at rest — **Critical: Protocol insolvency / direct theft**.

---

### Likelihood Explanation

- `pricePercentageLimit` defaults to `0` and requires an explicit admin call to `setPricePercentageLimit` to activate the circuit-breaker. Any deployment that omits this step is permanently vulnerable.
- LST depegging events (stETH, cbETH, rETH) are historically documented. A Chainlink feed correctly reporting a severely depegged price is a realistic, non-adversarial trigger — it does not require oracle operator compromise.
- `updateRSETHPrice()` is public; the attacker controls the timing of the price commit.
- The attacker's deposit only needs to exceed `minAmountToDeposit`; `minRSETHAmountExpected` can be set to `0`.

---

### Recommendation

1. **Add a minimum price floor in `ChainlinkPriceOracle.getAssetPrice`**: revert if the returned price is below a configurable threshold (e.g., `0.5e18`).
2. **Remove the `pricePercentageLimit > 0` guard from the downside circuit-breaker**: the pause should trigger unconditionally when the price drop exceeds a hard-coded minimum threshold, independent of whether `pricePercentageLimit` has been configured.
3. **Initialize `pricePercentageLimit` to a non-zero value** in the initializer (e.g., `1e16` = 1%).
4. **Add a staleness / sanity check in `_updateRsETHPrice`**: revert if `newRsETHPrice < previousPrice * MIN_PRICE_RATIO` rather than silently writing the bad price.

---

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction

// 1. Deploy protocol with pricePercentageLimit == 0 (default, never set)
// 2. Seed: 1000 stETH deposited by Alice → rsETHPrice ≈ 1e18

// 3. Set mock Chainlink feed for stETH to return answer = 1, decimals = 8
//    → ChainlinkPriceOracle.getAssetPrice(stETH) = 1e10

// 4. Attacker calls LRTOracle.updateRSETHPrice()
//    → totalETHInProtocol ≈ 1000e18 * 1e10 / 1e18 = 1000e10 (near-zero)
//    → newRsETHPrice = 1000e10 / rsethSupply ≈ 1e10
//    → pricePercentageLimit == 0 → isPriceDecreaseOffLimit = false → no pause
//    → rsETHPrice = 1e10  ✓

// 5. Attacker deposits 1 rETH (oracle still returns ~1e18 for rETH)
//    rsethAmountToMint = (1e18 * 1e18) / 1e10 = 1e26
//    Attacker receives 1e26 rsETH for 1 rETH

// 6. Assert: attacker's rsETH >> Alice's rsETH despite 1 rETH << 1000 stETH deposit
//    → attacker redeems, draining Alice's collateral

// Key assertions:
assertGt(rsETH.balanceOf(attacker), rsETH.balanceOf(alice) * 1e6);
assertLt(lrtDepositPool.getTotalAssetDeposits(rETH_addr), 2e18); // only 1 rETH deposited
```

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L101-108)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
