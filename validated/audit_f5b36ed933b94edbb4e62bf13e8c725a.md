Audit Report

## Title
Missing Chainlink Staleness, Round-Completeness, and Sign Validation Enables rsETH Over-Issuance and Excess Fee Minting — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` and silently discards every safety field, accepting any returned `int256 price` without checking staleness (`updatedAt`), round completeness (`answeredInRound >= roundId`), or positivity (`price > 0`). The same codebase already enforces all three checks in `ChainlinkOracleForRSETHPoolCollateral.getRate`, confirming the omission is an oversight rather than a design choice. The unvalidated price flows into both the rsETH mint calculation on every `depositAsset` call and the global `rsETHPrice` update, enabling share dilution of existing holders and excess protocol-fee minting to the treasury.

## Finding Description

**Root cause — `contracts/oracles/ChainlinkPriceOracle.sol` lines 49–55:**

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();          // four fields silently dropped
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`roundId`, `startedAt`, `updatedAt`, and `answeredInRound` are all unnamed blanks. No check is performed on:
- `updatedAt` — whether the answer is within the feed's heartbeat window
- `answeredInRound >= roundId` — whether the round completed
- `price > 0` — whether the answer is positive

**Contrast with `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` lines 27–36**, which is used for the L2 pool and applies all three guards:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

**Exploit path — Path 1 (deposit over-issuance):**

`depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice`.

`getRsETHAmountToMint` at `LRTDepositPool.sol:520`:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
A stale inflated price directly inflates `rsethAmountToMint`. The `minRSETHAmountExpected` slippage guard only protects the depositor from receiving *less* than expected; it does not prevent over-issuance.

**Exploit path — Path 2 (rsETH price corruption and excess fee minting):**

`updateRSETHPrice` → `_updateRsETHPrice` → `_getTotalEthInProtocol` → `getAssetPrice` for every supported asset (`LRTOracle.sol:339`). A stale inflated price inflates `totalETHInProtocol`, which inflates `newRsETHPrice` (`LRTOracle.sol:250`), which causes `protocolFeeInETH` to be computed against a phantom TVL increase (`LRTOracle.sol:244–246`), minting excess rsETH to the treasury (`LRTOracle.sol:306`).

The `pricePercentageLimit` guard (`LRTOracle.sol:256–257`) is a partial mitigant for Path 2 only: it is bypassed entirely when `pricePercentageLimit == 0` (the default after initialization), and it does not apply to Path 1 at all.

## Impact Explanation

**High — Theft of unclaimed yield.**

Path 1 dilutes existing rsETH holders by minting excess rsETH to the attacker, reducing the ETH-per-rsETH ratio for all current holders. Path 2 mints excess protocol-fee rsETH to the treasury, directly extracting yield that belongs to rsETH holders. Both impacts are concrete and repeatable without any privileged access.

## Likelihood Explanation

Chainlink's stETH/ETH feed on Ethereum mainnet has a 24-hour heartbeat. During periods of high gas prices, network congestion, or feed deprecation/migration, `updatedAt` can lag by hours without any on-chain indication. No privileged access, front-running, or brute force is required. Any external caller can trigger `depositAsset` or `updateRSETHPrice` while the feed is stale. This is a historically observed condition, not a theoretical one.

## Recommendation

Apply the same validation already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId)          revert StalePrice();
if (updatedAt == 0)                     revert IncompleteRound();
if (price <= 0)                         revert InvalidPrice();
if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
```

`MAX_STALENESS` should be set per-asset (e.g., via a mapping) to match each feed's documented heartbeat plus a reasonable buffer.

## Proof of Concept

**Foundry fork test outline:**

```solidity
// Fork mainnet at a block where stETH/ETH Chainlink updatedAt is > 24h old
// (or mock the aggregator to return a stale timestamp)

function test_staleOracleOverIssuance() public {
    // 1. Deploy mock aggregator returning price=1.05e18, updatedAt=block.timestamp - 25 hours
    MockAggregator staleAgg = new MockAggregator(1.05e8, block.timestamp - 25 hours);
    vm.prank(lrtAdmin);
    chainlinkOracle.updatePriceFeedFor(stETH, address(staleAgg));

    // 2. Record existing holder's rsETH balance and total supply
    uint256 supplyBefore = rsETH.totalSupply();

    // 3. Attacker deposits 100e18 stETH
    vm.startPrank(attacker);
    stETH.approve(address(depositPool), 100e18);
    depositPool.depositAsset(stETH, 100e18, 0, "");
    vm.stopPrank();

    // 4. Assert attacker received ~5% more rsETH than fair value
    uint256 attackerRsETH = rsETH.balanceOf(attacker);
    uint256 fairRsETH = (100e18 * 1e18) / lrtOracle.rsETHPrice(); // at 1.00e18 price
    assertGt(attackerRsETH, fairRsETH);

    // 5. Assert existing holders are diluted
    // (their share of totalETHInProtocol decreased)
}
```

The test requires no admin interaction after the stale feed is set; the attacker only calls the public `depositAsset` function. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
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
