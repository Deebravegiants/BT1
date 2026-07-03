### Title
Missing Chainlink Staleness Check in `ChainlinkPriceOracle` Allows Stale LST Price to Corrupt `rsETHPrice`, Enabling Profitable Deposit at Expense of Existing Holders - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` timestamp and `answeredInRound` values. A stale Chainlink feed for any supported LST (e.g., stETH/ETH) causes `LRTOracle._getTotalEthInProtocol()` to undercount protocol TVL, which in turn lowers the stored `rsETHPrice`. Because `updateRSETHPrice()` is public and callable by anyone, an attacker can deliberately trigger a price update while a feed is stale, then deposit a correctly-priced asset to receive more rsETH than fair value, and finally redeem after the price corrects — extracting value from existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the `price` field from `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-54
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The `updatedAt` timestamp and `answeredInRound` are completely ignored. No check of the form `require(block.timestamp - updatedAt < MAX_DELAY)` or `require(answeredInRound >= roundId)` exists.

This oracle is consumed by `LRTOracle._getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L336-343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // ← stale price accepted here
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
```

`_getTotalEthInProtocol()` feeds directly into `_updateRsETHPrice()`, which stores the result in the public `rsETHPrice` state variable:

```solidity
// contracts/LRTOracle.sol L250, L313
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;
```

`rsETHPrice` is then used in `LRTDepositPool.getRsETHAmountToMint()` to determine how many rsETH tokens a depositor receives:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Critically, `updateRSETHPrice()` is **public** — any external caller can trigger a price update at will:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The codebase itself demonstrates awareness of this class of bug: `ChainlinkOracleForRSETHPoolCollateral` (used in the L2 pool system) implements all three staleness guards that `ChainlinkPriceOracle` omits:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

---

### Impact Explanation

When a Chainlink LST/ETH feed (e.g., stETH/ETH) goes stale at a price lower than the true market price:

1. `_getTotalEthInProtocol()` underestimates the protocol's TVL.
2. `rsETHPrice` is written as a value lower than its true fair value.
3. A depositor of any correctly-priced asset (e.g., ETH or rETH whose feed is live) receives `amount * correctAssetPrice / staleLowRsETHPrice` rsETH — more than fair value.
4. Once the stale feed updates, `rsETHPrice` rises back to its correct level.
5. The attacker redeems rsETH and receives more ETH than deposited, extracting value from existing rsETH holders whose share is diluted.

Impact: **High — theft of unclaimed yield / dilution of existing rsETH holders**.

---

### Likelihood Explanation

Chainlink feeds can go stale due to:
- Network congestion preventing keeper updates.
- Sequencer downtime on L2 chains where the pool contracts are deployed.
- Deviation-threshold-based feeds not updating during low-volatility periods that are followed by sudden moves.

Because `updateRSETHPrice()` is public, the attacker does not need to wait for an organic price update — they can call it themselves the moment a feed is stale, making the timing fully attacker-controlled. The inconsistency between `ChainlinkOracleForRSETHPoolCollateral` (which has staleness guards) and `ChainlinkPriceOracle` (which does not) confirms this is an oversight rather than an intentional design choice.

Likelihood: **Medium**.

---

### Recommendation

Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
uint256 public constant MAX_PRICE_AGE = 1 hours; // configurable per asset

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price: round not complete");
    require(updatedAt != 0, "Stale price: incomplete round");
    require(price > 0, "Invalid price");
    require(block.timestamp - updatedAt <= MAX_PRICE_AGE, "Stale price: too old");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

**Setup**: Protocol holds 1000 stETH (true price 0.99 ETH) and 100 rETH (true price 1.05 ETH). rsETH supply = 1000. True `rsETHPrice` ≈ 1.095 ETH.

**Attack**:
1. stETH/ETH Chainlink feed goes stale at 0.90 ETH (true = 0.99 ETH).
2. Attacker calls `updateRSETHPrice()`:
   - `totalETHInProtocol` = 1000×0.90 + 100×1.05 = 1005 ETH (true = 1095 ETH).
   - `rsETHPrice` = 1005/1000 = 1.005 ETH (true ≈ 1.095 ETH).
3. Attacker deposits 100 ETH (price = 1.0 ETH, correct):
   - `rsethAmountToMint` = 100 × 1.0 / 1.005 ≈ **99.5 rsETH** (fair value ≈ 91.3 rsETH).
4. Chainlink feed updates to 0.99 ETH.
5. Attacker calls `updateRSETHPrice()`:
   - `totalETHInProtocol` = 1000×0.99 + 100×1.05 + 100 = 1195 ETH.
   - `rsETHPrice` = 1195/1099.5 ≈ 1.087 ETH.
6. Attacker redeems 99.5 rsETH → receives ≈ **108.2 ETH** (deposited 100 ETH).

Net profit ≈ 8.2 ETH extracted from existing rsETH holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
