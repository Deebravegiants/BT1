### Title
`ChainlinkPriceOracle.getAssetPrice()` Missing Price Staleness Validation Enables Stale Price in Deposit and Withdrawal Paths - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards both `updatedAt` and `answeredInRound`, performing zero staleness validation. This price is consumed directly by the deposit minting path and the withdrawal payout path, meaning a stale LST/ETH price can cause incorrect rsETH minting or incorrect asset redemption amounts for all users.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The return tuple from `latestRoundData()` is `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The function captures only `price` (the `answer` field) and discards all other fields, including `updatedAt` (the timestamp of the last price update) and `answeredInRound` (used to detect incomplete rounds). No check of the form `block.timestamp - updatedAt <= heartbeat` is performed, and no `answeredInRound < roundId` check is performed.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository does perform partial validation:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle.getAssetPrice()` performs none of these checks.

The stale price then propagates through two critical user-facing paths:

**Deposit path:**
`LRTDepositPool.depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()`

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Withdrawal path:**
`LRTWithdrawalManager.initiateWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()`

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**rsETH price update path:**
`LRTOracle.updateRSETHPrice()` (public, callable by anyone) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` for every supported asset.

---

### Impact Explanation

**Impact: Medium**

If a Chainlink LST/ETH price feed goes stale (e.g., stETH/ETH or ETHx/ETH):

- **Stale inflated price during deposit:** A depositor mints more rsETH than the fair value of their deposited LST. This dilutes existing rsETH holders, constituting theft of unclaimed yield from the protocol's existing depositor base.
- **Stale deflated price during withdrawal initiation:** `getExpectedAssetAmount()` returns a higher asset payout than warranted, allowing a withdrawer to claim more LST than their rsETH entitles them to, draining protocol assets.
- **Stale price during `updateRSETHPrice()`:** The computed `totalETHInProtocol` is incorrect, causing the stored `rsETHPrice` to be set to a wrong value, which then affects all subsequent deposits and withdrawals until corrected.

The impact is at minimum "Contract fails to deliver promised returns" and at maximum "Theft of unclaimed yield" (High) depending on the direction of the stale deviation.

---

### Likelihood Explanation

**Likelihood: Medium**

Chainlink LST/ETH price feeds (e.g., stETH/ETH, ETHx/ETH) typically have a 24-hour heartbeat. During periods of Ethereum network congestion, oracle keeper failures, or sequencer issues on L2, the feed can go stale for hours without triggering any on-chain revert. The absence of any staleness guard means the protocol silently accepts any price returned by `latestRoundData()` regardless of age. Any unprivileged depositor or withdrawer can exploit the window by calling `depositAsset()` or `initiateWithdrawal()` while the stale price is active.

---

### Recommendation

Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral.getRate()` and extending it with a time-based heartbeat check:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > HEARTBEAT_DURATION) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The `HEARTBEAT_DURATION` should be configurable per asset or set to a safe upper bound (e.g., 25 hours for 24-hour heartbeat feeds).

---

### Proof of Concept

1. Assume stETH/ETH Chainlink feed has a 24-hour heartbeat and last updated 25 hours ago (stale), returning a price of `1.05e18` (5% above current true value of `1.00e18`).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
3. `getRsETHAmountToMint()` computes: `rsethAmountToMint = (100e18 * 1.05e18) / rsETHPrice`.
4. Attacker receives ~5% more rsETH than fair value, diluting all existing rsETH holders.
5. No revert occurs because `ChainlinkPriceOracle.getAssetPrice()` performs no staleness check. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
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
