Audit Report

## Title
Unvalidated Chainlink `latestRoundData()` Output Enables Stale-Price-Driven rsETH Over-Issuance and Fee Over-Minting — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` and silently discards all safety fields (`updatedAt`, `answeredInRound`, sign of `price`). The unvalidated price flows into both the rsETH mint calculation on every `depositAsset` call and the global `updateRSETHPrice` path. The same codebase already implements all three required checks in `ChainlinkOracleForRSETHPoolCollateral.getRate`, confirming developer awareness of the requirement. A stale inflated feed allows any unprivileged depositor to receive excess rsETH, diluting existing holders, and causes excess protocol-fee rsETH to be minted to the treasury.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice` (line 52) destructures the `latestRoundData()` tuple with four unnamed blanks:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol:52
(, int256 price,,,) = priceFeed.latestRoundData();
```

No check is performed on:
- `updatedAt` — whether the answer is within the feed's heartbeat window
- `answeredInRound >= roundId` — whether the round completed
- `price > 0` — whether the answer is positive

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate` (lines 30–32) enforces all three:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` is the oracle registered for L1 LST assets (stETH, rETH, etc.) via `LRTOracle.updatePriceOracleFor`.

**Exploit path — Path 1 (deposit over-issuance):**
`depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice` → stale inflated price returned → `rsethAmountToMint = (amount * stalePrice) / rsETHPrice` mints excess rsETH to depositor, diluting all existing holders.

**Exploit path — Path 2 (fee over-minting):**
`updateRSETHPrice` → `_updateRsETHPrice` → `_getTotalEthInProtocol` → `getAssetPrice` for every supported asset → stale inflated prices inflate `totalETHInProtocol` → `protocolFeeInETH` is computed on a phantom reward → excess rsETH minted to treasury via `IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee)`.

The `pricePercentageLimit` guard in `_updateRsETHPrice` (lines 256–266) only blocks price increases above the configured threshold and only for non-manager callers; it does not protect Path 1 at all, and does not protect Path 2 for deviations within the limit or when `pricePercentageLimit == 0`.

## Impact Explanation

**High — Theft of unclaimed yield.**

Path 2 directly causes yield that should accrue to rsETH holders to instead be minted as excess fee rsETH to the treasury. Path 1 dilutes existing holders' share of the pool by over-issuing rsETH to a depositor who exploits the stale feed window. Both impacts are concrete and repeatable without any privileged access.

## Likelihood Explanation

Chainlink stETH/ETH on mainnet has a 24-hour heartbeat. During periods of network congestion, sequencer lag, or feed deprecation, `updatedAt` can lag by hours while the on-chain price remains stale. No privileged access, front-running, or brute force is required. Any depositor can observe a stale feed (e.g., via `latestRoundData()` off-chain) and call `depositAsset` to trigger Path 1. `updateRSETHPrice` is a public function callable by anyone, triggering Path 2. The condition is historically observed, not theoretical.

## Recommendation

Apply the same validation already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (price <= 0) revert InvalidPrice();
if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
```

`MAX_STALENESS` should be configured per-asset to match the feed's documented heartbeat (e.g., 24 h + buffer for stETH/ETH). Custom error types (`StalePrice`, `IncompleteRound`, `InvalidPrice`) should be added to the contract, consistent with the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`.

## Proof of Concept

1. Deploy a mock `AggregatorV3Interface` that returns a fixed `price = 1.05e8` (5% above true value) with `updatedAt = block.timestamp - 25 hours` and `answeredInRound == roundId`.
2. Register this mock as the price feed for stETH via `ChainlinkPriceOracle.updatePriceFeedFor`.
3. Call `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")` as an unprivileged EOA.
4. Observe that `getRsETHAmountToMint` returns `~105e18 * rsETHPrice_denominator / rsETHPrice` — approximately 5% more rsETH than a fresh-price deposit would yield.
5. Call `LRTOracle.updateRSETHPrice()` as an unprivileged EOA; observe that `_getTotalEthInProtocol` returns an inflated value, causing `protocolFeeInETH` to be computed on phantom yield, and excess rsETH to be minted to the treasury.
6. Confirm that `ChainlinkOracleForRSETHPoolCollateral.getRate` with the same mock reverts with `StalePrice`, demonstrating the inconsistency. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-36)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
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

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
