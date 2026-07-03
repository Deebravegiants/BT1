### Title
Stale/Invalid Chainlink Price Accepted Without Validation in `ChainlinkPriceOracle.getAssetPrice`, Corrupting rsETH Mint Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but discards all validity fields (`updatedAt`, `answeredInRound`, sign of `answer`). A stale or invalid Chainlink price propagates unchecked into `LRTOracle._getTotalEthInProtocol()`, corrupts the stored `rsETHPrice`, and causes every subsequent depositor to receive an incorrect amount of rsETH — either inflated (protocol insolvency) or deflated (theft of depositor value).

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

Three fields returned by `latestRoundData` are silently discarded:
- `updatedAt` — not checked against a staleness threshold, so a price that has not been updated for hours or days is accepted as current.
- `answeredInRound` — not compared to `roundId`, so an incomplete round is accepted.
- `answer` sign — cast directly to `uint256`; a negative `int256` wraps to a near-`type(uint256).max` value.

The protocol's own newer oracle wrapper, `ChainlinkOracleForRSETHPoolCollateral`, demonstrates the correct pattern:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle registered for L1 LST assets (stETH, ETHx, rETH, etc.) via `LRTOracle.assetPriceOracle`. `LRTOracle.getAssetPrice` delegates directly to it:

```solidity
return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
``` [3](#0-2) 

`_getTotalEthInProtocol` iterates every supported asset and multiplies its balance by the price returned from `getAssetPrice`:

```solidity
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [4](#0-3) 

`_updateRsETHPrice` uses this total to compute and store the new `rsETHPrice`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;
``` [5](#0-4) 

`updateRSETHPrice()` is a **public, permissionless** function:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [6](#0-5) 

Any depositor can call it at any time, including immediately after a Chainlink feed goes stale, to lock in a corrupted `rsETHPrice` before depositing.

---

### Impact Explanation

**Critical — direct theft of user funds / protocol insolvency.**

If a Chainlink feed for a high-TVL asset (e.g., stETH/ETH) goes stale and returns a price lower than the true market price, `totalETHInProtocol` is understated, `rsETHPrice` is pushed down, and every depositor who calls `depositAsset` or `depositETH` immediately after receives more rsETH than their deposit is worth. Repeated deposits drain the backing pool, causing insolvency for existing rsETH holders.

The reverse (inflated price) causes depositors to receive fewer rsETH tokens than they are entitled to — a direct loss of depositor value.

---

### Likelihood Explanation

**Medium.** Chainlink feeds do go stale during network congestion, L2 sequencer downtime, or oracle node failures. The permissionless `updateRSETHPrice()` means no privileged actor needs to be involved; any user can trigger the price update at the worst possible moment. The protocol holds significant TVL in stETH and ETHx, both of which use `ChainlinkPriceOracle`.

---

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
    // Optional: if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Chainlink stETH/ETH feed stops updating (e.g., sequencer downtime). `latestRoundData()` still returns the last stale answer with an old `updatedAt`.
2. Attacker observes the stale price is 10% below the true market price.
3. Attacker calls `LRTOracle.updateRSETHPrice()` (permissionless). `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)`, which returns the stale low price with no revert. `rsETHPrice` is written as 10% below true value.
4. Attacker calls `LRTDepositPool.depositAsset(stETH, largeAmount, 0, "")`. The mint calculation uses the deflated `rsETHPrice`, minting ~11% more rsETH than the deposit is worth.
5. Attacker redeems rsETH after the price corrects, extracting value from existing holders. [7](#0-6) [6](#0-5) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L250-313)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
        }

        // downside protection — pause if price drops too far
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

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

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
