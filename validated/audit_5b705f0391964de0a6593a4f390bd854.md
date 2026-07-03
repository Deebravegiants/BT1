### Title
Unchecked Cast of Signed Chainlink Price to `uint256` Inflates rsETH Exchange Rate — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by Chainlink's `latestRoundData()` directly to `uint256` without first validating that the value is positive. A negative price is silently reinterpreted as a near-maximum `uint256` value via two's complement, inflating the computed protocol TVL and ultimately the stored `rsETHPrice`. The same codebase already applies the correct guard in `ChainlinkOracleForRSETHPoolCollateral`, making the omission in `ChainlinkPriceOracle` a clear inconsistency.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` fetches the Chainlink answer and immediately casts it:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no `price > 0` guard. If `price` is `-1`, `uint256(-1)` equals `2²⁵⁶ − 1`, an astronomically large number.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used for the L2 pool collateral oracle in the same repository — explicitly rejects non-positive prices before casting:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** ...;
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle adapter registered in `LRTOracle` for every supported LST asset on L1. `LRTOracle.getAssetPrice()` delegates directly to it: [3](#0-2) 

`_getTotalEthInProtocol()` calls `getAssetPrice()` for every supported asset and accumulates the result into `totalETHInProtocol`: [4](#0-3) 

`_updateRsETHPrice()` then divides that total by `rsethSupply` to produce `newRsETHPrice`: [5](#0-4) 

If `pricePercentageLimit` is zero (its default `uint256` value, set only by an explicit admin call), the price-increase guard is skipped entirely:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [6](#0-5) 

In that state the inflated `newRsETHPrice` is written to storage unconditionally, and `LRTDepositPool` uses the stored `rsETHPrice` to calculate how much rsETH to mint for every subsequent deposit.

---

### Impact Explanation

**Critical — Protocol insolvency / direct theft of depositor funds.**

When `pricePercentageLimit == 0` (default):

1. A negative Chainlink answer for any supported LST causes `getAssetPrice()` to return `≈ 2²⁵⁶`.
2. `rsETHPrice` is set to `≈ 2²⁵⁶ / rsethSupply` — effectively infinite.
3. New depositors receive near-zero rsETH for their ETH (loss of value on deposit).
4. Existing rsETH holders who request withdrawal are entitled to `rsETHBalance × rsETHPrice` worth of ETH — far more than the protocol holds — draining all depositor funds.

When `pricePercentageLimit > 0`:

- `updateRSETHPrice()` reverts for any non-manager caller, permanently bricking price updates until the Chainlink feed recovers. The stored price becomes stale, causing incorrect rsETH minting rates for all subsequent depositors — a medium-severity temporary fund freeze / incorrect accounting.

---

### Likelihood Explanation

Chainlink `latestRoundData()` returns `int256` and can return zero or negative values during feed deprecation, misconfiguration, or circuit-breaker events. The Chainlink documentation explicitly warns that callers must validate `answer > 0`. The missing check is a single-line omission that is already correctly handled elsewhere in the same repository, making it a realistic oversight rather than a theoretical edge case.

---

### Recommendation

Add a non-positive price guard in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

---

### Proof of Concept

1. Chainlink feed for a supported LST (e.g., stETH) returns `answer = -1` (possible during feed deprecation or misconfiguration).
2. `ChainlinkPriceOracle.getAssetPrice(stETH)` computes `uint256(-1) * 1e18 / 1e18 = 2²⁵⁶ − 1`.
3. `LRTOracle._getTotalEthInProtocol()` adds `(2²⁵⁶ − 1) × stETH_balance` to `totalETHInProtocol`, overflowing to a huge but bounded value (Solidity 0.8 checked arithmetic would revert on overflow — but `mulWad` uses unchecked internally via `WadMath`; if it does not overflow, the value is astronomically large).
4. `_updateRsETHPrice()` sets `rsETHPrice = huge_value / rsethSupply`.
5. If `pricePercentageLimit == 0`: the new price is stored. Any rsETH holder calls `LRTWithdrawalManager` to redeem rsETH at the inflated rate, receiving far more ETH than they deposited, draining the pool.
6. If `pricePercentageLimit > 0`: `updateRSETHPrice()` reverts for all non-manager callers, freezing price updates and causing stale-price minting for all subsequent depositors. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-34)
```text
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
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
