### Title
Unvalidated Chainlink `latestRoundData()` Return Values in `ChainlinkPriceOracle.getAssetPrice()` Allow Stale/Invalid Price to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and uses the returned `price` directly without checking for staleness, round completeness, or a non-positive value. This is the price oracle plugged into the L1 deposit path. Because `updateRSETHPrice()` is publicly callable, any user can trigger a price update at a moment when the Chainlink feed is stale, permanently writing an incorrect `rsETHPrice` to storage. All subsequent deposits use that corrupted rate until the next valid update, causing either over-minting (protocol insolvency) or under-minting (theft of depositor yield).

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads from a Chainlink aggregator with no defensive checks:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Three return values are silently discarded: `roundId`, `updatedAt`, and `answeredInRound`. No check is made that:
- `answeredInRound >= roundId` (round completeness / staleness)
- `updatedAt > 0` (incomplete round)
- `price > 0` (valid price)

The same codebase already implements all three guards in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L26-36
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The unguarded oracle feeds directly into the publicly callable `updateRSETHPrice()`:

```
updateRSETHPrice()  [public, whenNotPaused]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ getAssetPrice(asset)          ← LRTOracle.sol L339
                 └─ IPriceFetcher.getAssetPrice(asset)
                      └─ ChainlinkPriceOracle.getAssetPrice()  ← stale price accepted
```

The computed `totalETHInProtocol` is then used to derive and **store** `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;   // L313 — persisted to storage
```

`rsETHPrice` is subsequently read by every deposit:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

---

### Impact Explanation

**Scenario A — stale price lower than actual (e.g., oracle heartbeat missed during a price rally):**
- `totalETHInProtocol` is underestimated → `rsETHPrice` is written too low.
- When the Chainlink feed recovers, `getAssetPrice(asset)` returns the correct (higher) value, but `rsETHPrice` is still stale-low.
- `rsethAmountToMint = amount * correct_high_price / stale_low_rsETHPrice` → depositors receive more rsETH than the protocol's assets back.
- Existing holders are diluted → **protocol insolvency (Critical)**.

**Scenario B — stale price higher than actual (e.g., oracle not yet reflecting a depeg):**
- `rsETHPrice` is written too high.
- Depositors receive fewer rsETH than they are entitled to → **theft of depositor yield (High)**.

**Scenario C — `price == 0` (deprecated or broken feed):**
- `uint256(0)` propagates through `_getTotalEthInProtocol()`, setting `rsETHPrice` to near-zero.
- All subsequent deposits mint a massive rsETH amount → **protocol insolvency (Critical)**.

---

### Likelihood Explanation

- `updateRSETHPrice()` is `public whenNotPaused` — any EOA or contract can call it at any time.
- Chainlink feeds have documented heartbeat intervals (e.g., 24 h for LST/ETH feeds). A stale window exists every cycle.
- On L2 deployments, sequencer downtime can freeze feed updates for hours while the contract remains callable.
- An attacker can monitor the mempool for a stale round and front-run the next legitimate update with a call that locks in the stale price.

Likelihood: **Medium**.

---

### Recommendation

Mirror the validation already present in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0)            revert IncompleteRound();
    if (price <= 0)                revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a configurable `maxStaleness` threshold (e.g., `block.timestamp - updatedAt > maxStaleness`) per feed.

---

### Proof of Concept

1. Assume the stETH/ETH Chainlink feed has a 24-hour heartbeat and its last update was 23 h 59 m ago (price = 0.998 ETH). The true current price is 1.002 ETH (not yet reflected).

2. Attacker calls `LRTOracle.updateRSETHPrice()`.

3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale 0.998 ETH.

4. `totalETHInProtocol` is underestimated; `rsETHPrice` is written to storage at a value ~0.4% below fair value.

5. Chainlink updates its feed to 1.002 ETH (heartbeat fires).

6. Attacker calls `LRTDepositPool.depositAsset(stETH, largeAmount, 0, "")`.

7. `getRsETHAmountToMint` computes: `largeAmount * 1.002e18 / stale_low_rsETHPrice` → attacker receives ~0.8% excess rsETH relative to fair value.

8. Attacker redeems rsETH via the withdrawal path, extracting value from existing holders.

The attack is repeatable every heartbeat cycle and requires no privileged access. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
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

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L516-520)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
