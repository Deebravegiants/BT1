### Title
Missing Staleness Check on Chainlink Price Feed Allows Stale Rate to Drive rsETH Minting — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` timestamp. A Chainlink feed that has stopped updating returns a frozen (effectively constant) price, which is then used as if it were current to compute the rsETH/ETH exchange rate. This is the direct analog of the external report: a value that must be dynamic is treated as always valid, causing systematic mis-accounting for every depositor.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink answer and immediately discards all staleness metadata:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is used; `updatedAt` and `answeredInRound` are thrown away. There is no check of the form `require(block.timestamp - updatedAt <= MAX_STALENESS, "stale")`.

This price is consumed by `LRTOracle._getTotalEthInProtocol()`, which iterates over every supported LST asset and multiplies its total deposit amount by the Chainlink-sourced price to compute `totalETHInProtocol`. That figure directly determines `newRsETHPrice`, which is then broadcast cross-chain via LayerZero to every L2 pool (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`) and used to mint wrsETH/rsETH to depositors.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / share mis-accounting**

If a Chainlink feed for a supported LST (e.g., stETH/ETH, rETH/ETH) becomes stale while the real price has risen:

- `_getTotalEthInProtocol()` understates the true ETH value of protocol assets.
- `newRsETHPrice` is computed lower than the true rate.
- Every subsequent depositor calling `deposit()` on any L2 pool receives `amountAfterFee * 1e18 / rsETHToETHrate` rsETH, where the denominator is artificially low → they receive **more rsETH than their ETH is worth**.
- This dilutes the rsETH holdings of all existing stakers, transferring yield from them to new depositors — a classic share-inflation attack enabled by a frozen oracle.

Conversely, if the stale price is above the true price, depositors receive fewer rsETH than owed, causing them to lose value silently.

---

### Likelihood Explanation

**Likelihood: Medium**

Chainlink feeds can go stale due to:
- L2 sequencer downtime (Arbitrum, Optimism, Base all have sequencer-dependent feeds).
- Feed deprecation or migration without contract update.
- Extreme network congestion preventing heartbeat updates.

The protocol operates on multiple L2s and mainnet, increasing the surface area. The `LRTOracle.updateRSETHPrice()` is callable by anyone (`public`), so an attacker can time a call to `updateRSETHPrice()` immediately after a feed goes stale but before it recovers, locking in the bad price that then propagates cross-chain.

---

### Recommendation

Add a staleness guard in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= MAX_STALENESS_SECONDS, "Stale price");
require(price > 0, "Non-positive price");

return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`MAX_STALENESS_SECONDS` should be set per-feed based on its documented heartbeat (e.g., 3600 s for a 1-hour heartbeat feed). Additionally, for L2 deployments, integrate a Chainlink sequencer uptime feed check before trusting any price.

---

### Proof of Concept

1. Chainlink stETH/ETH feed on mainnet stops updating (heartbeat missed). `updatedAt` is now 2+ hours old; real stETH price has risen 0.5%.

2. Anyone calls `LRTOracle.updateRSETHPrice()`:
   - `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → returns the stale (lower) price.
   - `totalETHInProtocol` is understated by ~0.5% of the stETH TVL.
   - `newRsETHPrice` is computed lower than the true rate.

3. The updated (deflated) `rsETHPrice` is broadcast via `CrossChainRateProvider` → LayerZero → `CrossChainRateReceiver` on every L2.

4. On L2, a depositor calls `RSETHPoolV3.deposit{value: 100 ether}("")`:
   - `viewSwapRsETHAmountAndFee(100 ether)` uses the deflated rate.
   - Depositor receives more wrsETH than 100 ETH is worth at the true rate.

5. When the Chainlink feed recovers and `updateRSETHPrice()` is called again, the true (higher) rsETH price is restored, but the extra wrsETH already minted remains — diluting all prior holders.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
