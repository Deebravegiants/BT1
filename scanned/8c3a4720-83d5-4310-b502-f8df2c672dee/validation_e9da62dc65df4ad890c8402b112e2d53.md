### Title
Missing Staleness Check on Chainlink `latestRoundData` Enables Fee Minting on Stale Inflated Prices — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but discards `updatedAt`, accepting arbitrarily stale prices. When a Chainlink feed goes stale at a price higher than the actual current price, a subsequent call to the public `updateRSETHPrice()` computes an inflated `totalETHInProtocol`, triggering fee minting to the treasury for yield that never occurred, diluting rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice` fetches the price as follows: [1](#0-0) 

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The `updatedAt` and `answeredInRound` return values are silently discarded. No maximum staleness threshold is enforced.

This price flows directly into `LRTOracle._getTotalEthInProtocol`: [2](#0-1) 

```solidity
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

And `_updateRsETHPrice` mints protocol fees whenever `totalETHInProtocol > previousTVL`: [3](#0-2) 

```solidity
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

`updateRSETHPrice()` is a permissionless `public` function: [4](#0-3) 

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

**Exploit path:**

1. At T0: Chainlink feed shows price P0. `updateRSETHPrice()` is called; `rsETHPrice` is set to reflect P0.
2. Between T0 and T1: Chainlink feed updates to P1 > P0 (genuine yield), but `updateRSETHPrice()` is **not** called.
3. At T1: The actual LST price drops from P1 back toward P0 (e.g., slashing event, market correction). The Chainlink feed **stops updating** (heartbeat missed, L2 sequencer down) and remains frozen at P1.
4. At T2: Anyone calls `updateRSETHPrice()`. `_getTotalEthInProtocol()` uses the stale P1 (inflated). `previousTVL = rsethSupply × rsETHPrice` (anchored at P0). Since P1 > P0, `totalETHInProtocol > previousTVL`, and protocol fee is minted to the treasury for the phantom P0→P1 gain, even though the actual current price is below P1.

The rsETH minted to the treasury dilutes all existing rsETH holders, transferring their unclaimed yield to the treasury.

---

### Impact Explanation

Excess rsETH is minted to the treasury proportional to `(stalePriceP1 − actualPriceP2) × totalDeposits × feeRate`. rsETH holders receive less ETH per rsETH than they are entitled to. This is a direct, quantifiable transfer of unclaimed yield from holders to the treasury. The `maxFeeMintAmountPerDay` cap bounds per-day damage but does not prevent the exploit. [5](#0-4) 

---

### Likelihood Explanation

- Chainlink heartbeat misses are a documented operational risk, especially on L2 networks where sequencer downtime is a known event.
- `updateRSETHPrice()` is permissionless — any address can trigger it at the worst moment.
- No oracle freshness validation exists anywhere in the call chain.
- The `pricePercentageLimit` guard only reverts if the price increase exceeds the configured threshold; small stale-price deltas pass through silently. [6](#0-5) 

---

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice`, validate `updatedAt` against a configurable maximum staleness:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > maxStaleness[asset]) revert StalePrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Store a per-asset `maxStaleness` value set by the LRT manager, aligned with each feed's published heartbeat interval.

---

### Proof of Concept

```solidity
// Fork test (local fork, no public-mainnet calls)
function test_stalePriceCausesPhantomFeeMint() external {
    // 1. Deploy mock Chainlink feed returning P0 with fresh updatedAt
    MockAggregator feed = new MockAggregator(P0, block.timestamp);
    oracle.updatePriceFeedFor(asset, address(feed));

    // 2. Anchor rsETHPrice at P0
    lrtOracle.updateRSETHPrice();

    // 3. Simulate: feed updated to P1 > P0, then froze 2 days ago
    feed.setPrice(P1);
    feed.setUpdatedAt(block.timestamp - 2 days);
    vm.warp(block.timestamp + 2 days); // advance time; actual price is still P0

    // 4. Anyone calls updateRSETHPrice — no staleness revert
    vm.expectEmit(true, true, false, false);
    emit FeeMinted(treasury, /* amount > 0 */ 1);
    lrtOracle.updateRSETHPrice(); // passes; fee minted for phantom P0→P1 gain
}
``` [7](#0-6) [8](#0-7)

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

**File:** contracts/LRTOracle.sol (L231-247)
```text
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
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
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
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
