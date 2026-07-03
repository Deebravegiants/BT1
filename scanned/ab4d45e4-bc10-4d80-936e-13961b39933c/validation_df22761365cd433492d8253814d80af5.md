### Title
Stale Chainlink Price Data Accepted Without Staleness Validation in `ChainlinkPriceOracle`, Enabling Incorrect rsETH Price Computation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` timestamp and `answeredInRound` fields, accepting arbitrarily stale prices. This stale price flows directly into `LRTOracle._getTotalEthInProtocol()` → `_updateRsETHPrice()`, causing the stored `rsETHPrice` to be set incorrectly. The same repository already demonstrates the correct pattern in `ChainlinkOracleForRSETHPoolCollateral`, making the omission in `ChainlinkPriceOracle` a clear inconsistency with a concrete impact path.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the `price` field from `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol line 52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The `updatedAt` timestamp and `answeredInRound` values are completely ignored. There is no check such as `require(updatedAt + heartbeat > block.timestamp)` or `require(answeredInRound >= roundId)`.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository performs both checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol lines 27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
```

`ChainlinkPriceOracle` is the price oracle used for all supported L1 LST assets (stETH, ethX, sfrxETH, etc.) registered in `LRTConfig`. Its output is consumed by `LRTOracle._getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol lines 339-343
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

`_getTotalEthInProtocol()` feeds directly into `_updateRsETHPrice()`, which computes and stores the canonical `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol line 250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

`updateRSETHPrice()` is a **public, permissionless function** — any external caller can invoke it at any time, including immediately after a Chainlink feed goes stale.

---

### Impact Explanation

**Scenario A — Stale price is lower than actual (e.g., LST appreciated but Chainlink hasn't updated):**
- `totalETHInProtocol` is underestimated.
- `newRsETHPrice` is set below the true value.
- Subsequent depositors via `LRTDepositPool` receive more rsETH per unit of LST than they are entitled to.
- This dilutes all existing rsETH holders, constituting **theft of unclaimed yield** (High impact).
- Additionally, the downside protection logic at lines 270–281 may trigger a false-positive pause, **temporarily freezing funds** for all users.

**Scenario B — Stale price is higher than actual (e.e., LST depegged but Chainlink hasn't updated):**
- `totalETHInProtocol` is overestimated.
- `newRsETHPrice` is set above the true value.
- New depositors receive fewer rsETH tokens than deserved — **contract fails to deliver promised returns** (Low impact).

The most severe path is Scenario A: an attacker or any user calls the public `updateRSETHPrice()` during a period of Chainlink feed staleness, locking in a deflated `rsETHPrice`, then immediately deposits LSTs to receive excess rsETH at the expense of all existing holders.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 hours for some LST/ETH feeds). During periods of low volatility, feeds may not update for the full heartbeat window. Network congestion, sequencer downtime on L2, or oracle operator issues can extend staleness further. Since `updateRSETHPrice()` is public and permissionless, any actor can trigger the price update at the worst possible moment. This is a realistic, externally reachable condition requiring no privileged access.

---

### Recommendation

Add staleness and round-completeness checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old");
require(price > 0, "Invalid price");
```

A per-asset configurable `MAX_STALENESS` parameter should be introduced to accommodate different Chainlink feed heartbeat intervals.

---

### Proof of Concept

1. Chainlink feed for stETH/ETH goes stale (no update for >24 hours; last reported price is 5% below current market).
2. Any external caller invokes `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns the stale, deflated price without reverting.
4. `totalETHInProtocol` is underestimated by ~5% of the stETH TVL.
5. `newRsETHPrice` is set ~5% below the true value and stored in `rsETHPrice`.
6. Attacker immediately calls `LRTDepositPool.depositAsset(stETH, largeAmount)`, receiving ~5% more rsETH than the true exchange rate entitles them to.
7. When the Chainlink feed resumes and `rsETHPrice` is corrected upward, the attacker's excess rsETH represents a direct dilution of all pre-existing rsETH holders' share of the protocol TVL. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-251)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
