### Title
Missing Chainlink `updatedAt` Staleness Check Enables Inflated TVL, Unbacked Fee Minting, and Over-issuance of rsETH — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` return value. If a Chainlink LST/ETH feed becomes stale while the true asset price has dropped (e.g., a slashing event), the protocol accepts the frozen high price, computes an inflated TVL, mints unbacked fee rsETH to the treasury, and sets an elevated `rsETHPrice` — allowing subsequent depositors to receive more rsETH than their collateral is worth.

---

### Finding Description

**Root cause — `contracts/oracles/ChainlinkPriceOracle.sol` line 52:**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

All five return values are destructured; `updatedAt` (4th position) is discarded with no comparison against `block.timestamp`. [1](#0-0) 

**Call chain:**

1. `LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported asset. [2](#0-1) 

2. `_updateRsETHPrice()` uses the returned `totalETHInProtocol` to compute `newRsETHPrice`, calculate a `protocolFeeInETH`, mint fee rsETH to the treasury, and store the new price. [3](#0-2) 

3. `LRTDepositPool.getRsETHAmountToMint()` divides the stale asset price by the now-elevated `rsETHPrice` to determine how many rsETH tokens to issue. [4](#0-3) 

**Concrete numeric example:**

| State | Value |
|---|---|
| Protocol holds 100 stETH | — |
| True stETH/ETH price (post-slash) | 0.95 ETH |
| Stale Chainlink price (pre-slash) | 1.05 ETH |
| rsETH supply | 100 |
| Previous `rsETHPrice` | 1.00 ETH |
| `totalETHInProtocol` (stale) | 105 ETH (true: 95 ETH) |
| `previousTVL` | 100 ETH |
| Fake `rewardAmount` | 5 ETH |
| `protocolFeeInETH` (10% BPS) | 0.5 ETH → minted as unbacked rsETH |
| `newRsETHPrice` stored | (105 − 0.5) / 100 = **1.045 ETH** (true: ~0.95 ETH) |

A depositor who then calls `depositAsset(stETH, 1e18, ...)`:
- `getAssetPrice(stETH)` = 1.05 ETH (stale)
- `rsETHPrice` = 1.045 ETH (inflated)
- rsETH minted = 1.05 / 1.045 ≈ **1.0048 rsETH**
- True value of 1 stETH = 0.95 ETH → should mint ≈ 0.95 rsETH

The depositor receives ~5.8% excess rsETH. The treasury holds unbacked fee rsETH. The protocol is insolvent.

---

### Impact Explanation

**Critical — Protocol insolvency.**

- Treasury receives rsETH minted against a phantom "reward" that does not exist in real collateral.
- Every depositor who calls `depositAsset()` after the stale-price update receives rsETH in excess of their true collateral value.
- When the Chainlink feed corrects, `rsETHPrice` will drop, but the excess rsETH already minted remains outstanding and unbacked.

The `maxFeeMintAmountPerDay` guard limits the treasury fee mint per day but does **not** prevent the elevated `rsETHPrice` from being stored, nor does it prevent depositors from minting at the inflated rate. [5](#0-4) 

The `pricePercentageLimit` guard only fires when `pricePercentageLimit > 0`; it defaults to `0` and is a separately configured parameter. [6](#0-5) 

---

### Likelihood Explanation

**Medium.** The scenario requires two simultaneous conditions:

1. An LST experiences a real price drop (e.g., slashing, depeg) while the Chainlink feed has not yet updated. For stETH/ETH the Chainlink heartbeat is 24 hours with a 0.5% deviation threshold — a feed can legitimately be many hours old without any oracle operator failure.
2. `updateRSETHPrice()` is called during the staleness window. This function is **public and permissionless**. [7](#0-6) 

No admin compromise, no front-running, no governance capture is required. An attacker simply monitors for a slashing event, waits for the feed to lag, and calls `updateRSETHPrice()` followed by `depositAsset()`.

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
```

`MAX_STALENESS` should be set per-feed based on the Chainlink heartbeat (e.g., 25 hours for a 24-hour heartbeat feed). Additionally, validate that `price > 0` to guard against a zero/negative answer.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";

contract MockStaleFeed {
    int256 public answer;
    uint256 public updatedAt;
    uint8 public decimals_ = 18;

    constructor(int256 _answer, uint256 _updatedAt) {
        answer = _answer;
        updatedAt = _updatedAt;
    }

    function latestRoundData() external view returns (
        uint80, int256, uint256, uint256, uint80
    ) {
        return (1, answer, 0, updatedAt, 1);
    }

    function decimals() external view returns (uint8) { return decimals_; }
}

contract StalenessPoC is Test {
    // Fork mainnet, deploy protocol, set stale feed, call updateRSETHPrice(),
    // then depositAsset() and assert rsETH minted > true collateral value.

    function testStalePrice() public {
        // 1. Deploy MockStaleFeed with price = 1.05e18, updatedAt = block.timestamp - 48 hours
        MockStaleFeed staleFeed = new MockStaleFeed(
            1.05e18,
            block.timestamp - 48 hours
        );

        // 2. Wire staleFeed into ChainlinkPriceOracle for stETH
        // (via updatePriceFeedFor — requires LRTManager role in fork test)

        // 3. Call LRTOracle.updateRSETHPrice() — succeeds, no revert
        // lrtOracle.updateRSETHPrice();

        // 4. Assert rsETHPrice is elevated above true collateral ratio
        // assertGt(lrtOracle.rsETHPrice(), truePrice);

        // 5. Deposit 1 stETH, assert rsETH minted > 1 (true ratio ~0.95)
        // uint256 minted = depositPool.depositAsset(stETH, 1e18, 0, "");
        // assertGt(minted, 1e18); // receives more rsETH than collateral is worth
    }
}
```

The `getAssetPrice` call returns the stale price without any revert because `updatedAt` is never read. [1](#0-0)

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

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L231-313)
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

        // compute new rsETH price based on total ETH minus fee
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

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L516-520)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
