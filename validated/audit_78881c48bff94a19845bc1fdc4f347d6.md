### Title
No Staleness Validation on Chainlink Price Data Allows Stale LST Prices to Drive rsETH Minting — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards every return value except `price`. There is no check on `updatedAt`, `answeredInRound`, or any time-based freshness threshold. A stale Chainlink feed for any supported LST (stETH, ETH, etc.) will silently return an outdated price that is then used to calculate how many rsETH tokens to mint for a depositor, enabling over-minting at the expense of existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` is the price-fetching implementation registered in `LRTOracle` for supported LST assets:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (, int256 price,,,) = priceFeed.latestRoundData();   // ← updatedAt, answeredInRound silently discarded

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract binds only `price` (`answer`) and ignores the rest. There is no:
- `require(answeredInRound >= roundId)` — round-completeness check
- `require(updatedAt > 0)` — non-zero timestamp check
- `require(block.timestamp - updatedAt <= maxStaleness)` — time-based freshness check

This price is consumed by `LRTOracle.getAssetPrice()`:

```solidity
// contracts/LRTOracle.sol  line 156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

Which is called by `LRTDepositPool.getRsETHAmountToMint()` to determine how many rsETH tokens to mint:

```solidity
// contracts/LRTDepositPool.sol  line 519-521
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

Which is the core calculation inside `depositAsset()` and `depositETH()`, both publicly callable by any user:

```solidity
// contracts/LRTDepositPool.sol  line 99-118
function depositAsset(address asset, uint256 depositAmount, ...) external nonReentrant whenNotPaused ...
``` [4](#0-3) 

By contrast, the codebase's own `ChainlinkOracleForRSETHPoolCollateral` (used in L2 pools) demonstrates the team is aware of the need for staleness validation — it checks `answeredInRound < roundID` and `timestamp == 0` — yet the mainnet `ChainlinkPriceOracle` has none of these guards:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol  line 27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();

if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [5](#0-4) 

---

### Impact Explanation

If a Chainlink LST/ETH feed (e.g., stETH/ETH) becomes stale — its last `updatedAt` timestamp is older than the feed's heartbeat — the contract continues to return the last recorded price without any revert or warning. During a depeg or sharp price drop, the stale (higher) price causes `getRsETHAmountToMint` to compute a larger rsETH output than the deposited asset is currently worth. The attacker receives excess rsETH backed by insufficient collateral, diluting all existing rsETH holders and moving the protocol toward insolvency. This constitutes **theft of unclaimed yield / direct theft of user funds** (High–Critical).

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for stETH/ETH on mainnet). Staleness occurs during Ethereum network congestion, Chainlink node outages, or extreme market volatility — precisely the conditions under which LST prices move most sharply. An attacker monitoring on-chain feed timestamps can detect staleness and immediately exploit the window before the feed recovers. No privileged access is required; `depositAsset` is open to any address.

---

### Recommendation

Add staleness validation inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
uint256 public maxStaleness; // configurable by LRTManager

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale round");
    require(updatedAt > 0, "Incomplete round");
    require(block.timestamp - updatedAt <= maxStaleness, "Stale price");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`maxStaleness` should be set per-asset to match each feed's documented heartbeat, and should be configurable by the LRT manager role.

---

### Proof of Concept

1. Chainlink stETH/ETH feed on mainnet has a 1-hour heartbeat. Suppose the feed has not updated for 90 minutes (stale) and the last recorded price is `1.00 ETH` per stETH.
2. During this window, stETH depegs to `0.90 ETH` on the open market.
3. An attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `rsethAmountToMint = (1000e18 * 1.00e18) / rsETHPrice` — using the stale `1.00` price instead of the real `0.90`.
5. The attacker receives ~11% more rsETH than the deposited stETH is currently worth.
6. The attacker immediately sells or redeems the excess rsETH, extracting value from existing holders.
7. No admin action, no privileged key, and no oracle operator compromise is required — only monitoring the `updatedAt` field of the Chainlink feed. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-32)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```
