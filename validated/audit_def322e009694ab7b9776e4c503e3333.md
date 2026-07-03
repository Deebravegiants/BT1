### Title
Missing Chainlink Price Feed Validation Allows Stale or Zero Price to Corrupt rsETH Minting and Withdrawal Calculations - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validation fields (`roundId`, `updatedAt`, `answeredInRound`), and does not check whether the returned `price` is zero or negative. A stale or zero price propagates directly into rsETH minting and withdrawal payout calculations, causing depositors to receive zero rsETH for real assets or causing incorrect rsETH price updates across the protocol.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the asset/ETH exchange rate from a Chainlink aggregator:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

All five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The code destructures only `price` (the `answer`) and ignores the rest. There is no check for:
- `price <= 0` (zero or negative answer)
- `answeredInRound < roundId` (stale round)
- `updatedAt == 0` (incomplete round / uninitialized feed)
- Heartbeat staleness (`block.timestamp - updatedAt > heartbeat`)

By contrast, the sibling contract `ChainlinkOracleForRSETHPoolCollateral.getRate()` performs all three critical checks (`answeredInRound < roundID`, `timestamp == 0`, `ethPrice <= 0`), demonstrating the protocol is aware of the requirement but failed to apply it to `ChainlinkPriceOracle`.

`ChainlinkPriceOracle.getAssetPrice()` is the oracle backend registered in `LRTOracle` for supported LST assets (stETH, ETHx, etc.). `LRTOracle.getAssetPrice()` delegates directly to it:

```solidity
// contracts/LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
```

This price is consumed in two critical paths:

**Path 1 – Deposit minting:**
```solidity
// contracts/LRTDepositPool.sol L519-520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Path 2 – rsETH price update (TVL computation):**
```solidity
// contracts/LRTOracle.sol L339-343
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**Path 3 – Withdrawal payout:**
```solidity
// contracts/LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

### Impact Explanation
If `latestRoundData()` returns `price = 0` (e.g., uninitialized or malfunctioning feed):

- **Deposit path:** `rsethAmountToMint = (amount * 0) / rsETHPrice = 0`. The user's LST assets are transferred into the protocol but they receive 0 rsETH — a direct, permanent loss of deposited funds.
- **TVL path:** The affected asset's ETH value is counted as 0 in `_getTotalEthInProtocol`, causing `rsETHPrice` to be computed far below its true value. This can trigger the downside-protection pause (freezing the protocol) or allow subsequent depositors to mint rsETH at an artificially cheap rate, diluting existing holders.
- **Withdrawal path:** `lrtOracle.getAssetPrice(asset) = 0` causes division by zero, reverting all withdrawal unlocks for that asset — temporary freeze of withdrawal funds.

If `price` is negative (stale aggregator returning a sentinel), `uint256(int256_negative)` wraps to a near-`2^256` value, causing arithmetic overflow in `mulWad` and reverting all price-dependent operations.

**Impact:** Critical — direct loss of deposited user funds (zero rsETH minted for real assets) and/or temporary freeze of withdrawals.

### Likelihood Explanation
Low. Requires a Chainlink price feed to malfunction (return 0 or a stale answer). This can occur during feed initialization, aggregator migration, or a prolonged network outage where `answeredInRound < roundId`. The Chainlink documentation explicitly warns that `latestRoundData` can return stale data and recommends staleness checks. The likelihood matches the external report's assessment.

### Recommendation
Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optionally: if (block.timestamp - updatedAt > HEARTBEAT) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

### Proof of Concept

1. Chainlink's ETHx/ETH feed (or any supported LST feed) enters a degraded state and `latestRoundData()` returns `price = 0`.
2. Any user calls `LRTDepositPool.depositAsset(ETHx, 10 ether, 0)`.
3. `_beforeDeposit` calls `getRsETHAmountToMint(ETHx, 10 ether)`.
4. `getRsETHAmountToMint` calls `lrtOracle.getAssetPrice(ETHx)` → `ChainlinkPriceOracle.getAssetPrice(ETHx)` → returns `0`.
5. `rsethAmountToMint = (10e18 * 0) / rsETHPrice = 0`.
6. `minRSETHAmountExpected = 0` passes the slippage check.
7. 10 ETHx is transferred from the user to the protocol; user receives 0 rsETH.
8. User's 10 ETHx (~10 ETH in value) is permanently lost.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
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
