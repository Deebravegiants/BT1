Audit Report

## Title
Missing Chainlink Price Validity Checks in `ChainlinkPriceOracle.getAssetPrice()` Allows Stale/Invalid Prices to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validity fields, performing no staleness (`answeredInRound < roundId`), incomplete-round (`updatedAt == 0`), or non-positive price checks. The same repository already implements all three checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, making the omission a concrete inconsistency. Because `updateRSETHPrice()` is a public function, an attacker can trigger a price update at the exact moment a Chainlink feed is stale, permanently corrupting the stored `rsETHPrice` and diluting existing rsETH holders.

## Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` are available but only `answer` is used. No check is made for `answeredInRound < roundId` (stale round), `updatedAt == 0` (incomplete round), or `price <= 0` (invalid price).

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The exploit path is:

1. `updateRSETHPrice()` is public with no access control beyond `whenNotPaused`: [3](#0-2) 

2. It calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice(asset)`, which returns the stale price without reverting. [4](#0-3) 

3. The stale asset price directly determines `totalETHInProtocol`, which determines `newRsETHPrice` written to storage: [5](#0-4) 

4. The corrupted `rsETHPrice` is then used in `getExpectedAssetAmount()` (called by `initiateWithdrawal`) to compute how many rsETH tokens to mint per deposited asset: [6](#0-5) 

**Existing mitigations are insufficient:** The `pricePercentageLimit` guard (L256–266 and L270–282 of `LRTOracle.sol`) only triggers if `pricePercentageLimit > 0` AND the price deviation exceeds the configured threshold. If `pricePercentageLimit == 0` (its default uninitialized value), no protection exists at all. Even when set, a stale price within the configured band silently corrupts `rsETHPrice` without triggering any revert or pause. [7](#0-6) 

## Impact Explanation
**Stale-low asset price**: `totalETHInProtocol` is underestimated → `rsETHPrice` is set artificially low → subsequent depositors receive more rsETH than they are entitled to, diluting existing rsETH holders. This constitutes **theft of unclaimed yield** from existing holders (High severity per allowed impact scope).

**Stale-high asset price**: `rsETHPrice` is set artificially high → subsequent depositors receive fewer rsETH than entitled (Low: contract fails to deliver promised returns).

**Zero or negative price**: `uint256(negative_int256)` wraps to a very large number, causing catastrophic overestimation of `totalETHInProtocol`; a zero price causes `rsETHPrice` to collapse to zero, triggering the downside-protection pause — but only if `pricePercentageLimit > 0`.

The primary in-scope impact is **High — theft of unclaimed yield** via the stale-low scenario diluting existing rsETH holders.

## Likelihood Explanation
Chainlink feeds can temporarily return stale data during network congestion or when a feed's heartbeat has not been met. `updateRSETHPrice()` is a public function requiring no privileged access, so any external caller — including a bot — can invoke it at the precise moment a feed is stale. No victim mistake or privileged collusion is required. The condition is externally observable on-chain (by monitoring `answeredInRound` vs `roundId` on the Chainlink feed), making targeted exploitation realistic.

## Recommendation
Apply the same validity checks already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a per-feed configurable heartbeat check (`block.timestamp - updatedAt > heartbeat`) to guard against feeds that are technically in a valid round but have not been updated within their expected interval.

## Proof of Concept
1. Monitor the Chainlink LST/ETH feed until `answeredInRound < roundId` (stale round) due to network congestion.
2. Call `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice(asset)` returns the stale (artificially low) price without reverting.
4. `totalETHInProtocol` is underestimated; `newRsETHPrice` is written to `rsETHPrice` storage at an artificially low value.
5. Attacker (or any user) calls `LRTDepositPool.depositAsset()` immediately after; `getRsETHAmountToMint` uses the corrupted low `rsETHPrice` to mint excess rsETH, diluting all existing holders.
6. Existing rsETH holders have permanently lost a portion of their yield/value.

**Foundry fork test plan**: Fork mainnet, mock a Chainlink aggregator to return `answeredInRound = roundId - 1` with a price 5% below the true price (within a typical `pricePercentageLimit`), call `updateRSETHPrice()`, assert `rsETHPrice` is set to the stale-low value, then deposit and assert the minted rsETH exceeds the fair amount, confirming dilution of existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L231-250)
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
```

**File:** contracts/LRTOracle.sol (L252-267)
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

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
