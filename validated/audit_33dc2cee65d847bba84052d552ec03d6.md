### Title
Stale Chainlink Price Data Accepted Without Validation in `ChainlinkPriceOracle` — Incorrect rsETH Minting and TVL Accounting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, performing zero staleness, zero-price, or round-completeness checks. This stale price propagates directly into rsETH minting amounts for every depositor and into the protocol-wide rsETH/ETH price update callable by anyone.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice` function fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `price` (the `answer`) is used. There is no check that:
- `price > 0` (non-zero / non-negative)
- `answeredInRound >= roundId` (round is not stale)
- `updatedAt != 0` (round is complete)
- `block.timestamp - updatedAt <= heartbeat` (price is fresh)

By contrast, the sibling contract `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` does implement `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` checks — demonstrating the project is aware of the pattern but did not apply it to `ChainlinkPriceOracle`. [1](#0-0) [2](#0-1) 

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` is consumed by `LRTOracle.getAssetPrice()`, which is called in two critical paths:

1. **`LRTOracle._getTotalEthInProtocol()`** — iterates all supported LST assets, multiplies each asset's total deposit amount by its Chainlink price, and sums to compute total protocol ETH. This value directly determines `newRsETHPrice`.

2. **`LRTDepositPool.getRsETHAmountToMint()`** — used in both `depositETH()` and `depositAsset()` to compute how many rsETH tokens a depositor receives: `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()`. [3](#0-2) [4](#0-3) 

If a stale (deflated) price is consumed:
- `_getTotalEthInProtocol()` returns a lower-than-actual TVL.
- `newRsETHPrice` is set below its true value.
- Subsequent depositors receive **more rsETH than they are entitled to**, diluting existing rsETH holders — a direct theft of value from existing holders.

If a stale (inflated) price is consumed:
- Depositors receive **fewer rsETH tokens** than they are entitled to — a loss for the depositor.

`updateRSETHPrice()` is a public function with no access control, so any unprivileged caller can trigger the price update at any time, including during a period when the Chainlink feed is stale. [5](#0-4) 

---

### Likelihood Explanation

Chainlink feeds can return stale data during network congestion, oracle node downtime, or when the price has not moved enough to trigger a deviation update within the heartbeat window. The ETH/LST feeds used by this protocol (stETH/ETH, rETH/ETH, etc.) have heartbeats of 24 hours on mainnet. During that window, a stale price is a realistic on-chain condition. Because `updateRSETHPrice()` is permissionless, an attacker can deliberately call it during a known stale window to lock in a manipulated rsETH price, then immediately deposit to exploit the mispricing.

---

### Recommendation

Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`, and additionally add a heartbeat freshness check:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > HEARTBEAT) revert PriceTooOld();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Where `HEARTBEAT` is set per feed (e.g., 86 400 seconds for 24-hour feeds, 3 600 seconds for 1-hour feeds).

---

### Proof of Concept

1. Chainlink's stETH/ETH feed has not been updated for 23 hours (within its 24-hour heartbeat, so no circuit breaker fires). The last reported price is 0.97 ETH/stETH, but the true market price is 0.995 ETH/stETH.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (permissionless). `_getTotalEthInProtocol()` uses the stale 0.97 price, computing a lower TVL. `newRsETHPrice` is set below its true value (e.g., 1.04 ETH/rsETH instead of the correct 1.06 ETH/rsETH).
3. Attacker immediately calls `LRTDepositPool.depositAsset(stETH, largeAmount, ...)`. `getRsETHAmountToMint` computes: `rsethAmountToMint = (largeAmount * 0.97e18) / 1.04e18`. The attacker receives rsETH priced at the artificially depressed rate.
4. When the Chainlink feed updates to the correct price and `updateRSETHPrice()` is called again, `rsETHPrice` rises to reflect true TVL. The attacker's rsETH is now worth more than what they paid, at the expense of existing holders. [1](#0-0) [5](#0-4) [6](#0-5)

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
