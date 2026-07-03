### Title
No Staleness Check on Chainlink `latestRoundData()` Allows Stale Asset Prices to Drive rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and discards every return value except the raw price. There is no check on `updatedAt` (timestamp), `answeredInRound`, or price sign. If Chainlink OCR fails to push an update in time, the stale price is silently accepted and propagates into rsETH minting and the rsETH price update.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` is used. The following validations are entirely absent:

| Check | Purpose | Present? |
|---|---|---|
| `block.timestamp - updatedAt <= maxStaleness` | Reject prices older than threshold | No |
| `answeredInRound >= roundId` | Reject incomplete rounds | No |
| `price > 0` | Reject zero/negative prices | No |
| `updatedAt != 0` | Reject unstarted rounds | No |

By contrast, the sibling contract `ChainlinkOracleForRSETHPoolCollateral` in the same repository does perform `answeredInRound < roundID` and `timestamp == 0` checks, confirming the project is aware of these requirements but failed to apply them to `ChainlinkPriceOracle`. [1](#0-0) [2](#0-1) 

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` is the price source for every supported LST asset (stETH, cbETH, etc.). It feeds two critical paths:

1. **Deposit minting** — `LRTDepositPool.getRsETHAmountToMint()` divides `lrtOracle.getAssetPrice(asset)` by `lrtOracle.rsETHPrice()` to determine how many rsETH tokens a depositor receives.
2. **rsETH price update** — `LRTOracle._getTotalEthInProtocol()` multiplies each asset's total balance by `getAssetPrice(asset)` to compute TVL, which then sets the stored `rsETHPrice`. [3](#0-2) [4](#0-3) 

If a Chainlink feed goes stale with a price lower than the true market price (e.g., during a temporary OCR outage after a depeg recovery), TVL is understated, `rsETHPrice` is set too low, and every depositor calling `depositAsset` during that window mints more rsETH than they are entitled to. This dilutes the share value of all existing rsETH holders — a direct theft of their accrued yield. The inverse (stale high price) causes depositors to receive fewer rsETH tokens than owed.

Impact classification: **High — Theft of unclaimed yield** (existing rsETH holders lose value when over-minting occurs against a stale low price).

---

### Likelihood Explanation

Chainlink OCR feeds have documented heartbeat windows (typically 1 hour for ETH-denominated LST feeds). Network congestion, gas spikes, or OCR node failures can delay updates beyond the heartbeat. The condition is not attacker-controlled but is a realistic, externally observable network event. Any depositor transacting during the stale window automatically exploits the mispricing without any special action.

---

### Recommendation

Add a configurable `maxStaleness` parameter and validate all relevant fields from `latestRoundData()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(price > 0,                          "Invalid price");
require(updatedAt != 0,                     "Incomplete round");
require(answeredInRound >= roundId,         "Stale round");
require(block.timestamp - updatedAt <= maxStaleness, "Price too stale");
```

`maxStaleness` should be set per feed based on its documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed, with a small buffer).

---

### Proof of Concept

1. Chainlink OCR for the stETH/ETH feed fails to push an update for 2 hours. The last reported price is `0.998e18` (stETH slightly below peg).
2. The true market price recovers to `1.000e18`, but the on-chain feed still returns `0.998e18`.
3. `LRTOracle._getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `0.998e18`.
4. TVL is understated by 0.2% relative to true value → `rsETHPrice` is set 0.2% too low.
5. A depositor calls `LRTDepositPool.depositAsset(stETH, amount, ...)` → `getRsETHAmountToMint` uses the stale low `rsETHPrice` as denominator → depositor receives ~0.2% more rsETH than they should.
6. When the feed updates and `rsETHPrice` corrects upward, all pre-existing rsETH holders have been diluted by the over-minted tokens. [1](#0-0) [5](#0-4) [6](#0-5)

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
