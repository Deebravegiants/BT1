### Title
Stale Chainlink Price Accepted in `ChainlinkPriceOracle.getAssetPrice` Enables Phantom Fee Minting Against Inflated TVL — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but silently discards `updatedAt` and `answeredInRound`, accepting any price regardless of age. When a supported LST's Chainlink feed goes stale while the asset's true ETH value has declined, the stale (inflated) price overstates `totalETHInProtocol` in `_getTotalEthInProtocol`. The fee-minting branch in `_updateRsETHPrice` then treats the phantom TVL increase as real yield and mints rsETH to the treasury, diluting all rsETH holders.

---

### Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice`:**

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  lines 49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt & answeredInRound ignored
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`latestRoundData()` returns `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract destructures only `price`; `updatedAt` (position 4) and `answeredInRound` (position 5) are never read. There is no `require(updatedAt >= block.timestamp - MAX_STALENESS)` and no `require(answeredInRound >= roundId)` guard. [1](#0-0) 

Compare with the pool-side oracle in the same repo, which does perform these checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol  lines 27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [2](#0-1) 

The production `ChainlinkPriceOracle` used for LST pricing has no equivalent protection.

**Fee-minting path — `_updateRsETHPrice` / `_getTotalEthInProtocol`:**

`_getTotalEthInProtocol` iterates every supported asset and calls `getAssetPrice(asset)`, which routes to `ChainlinkPriceOracle.getAssetPrice` for Chainlink-backed LSTs. The stale inflated price is multiplied by the total deposited amount, overstating `totalETHInProtocol`. [3](#0-2) 

Back in `_updateRsETHPrice`, if `totalETHInProtocol > previousTVL`, the difference is treated as real yield and a protocol fee is computed and minted:

```solidity
// contracts/LRTOracle.sol  lines 244-247
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
``` [4](#0-3) 

The fee is then minted to the treasury as rsETH: [5](#0-4) 

**Partial mitigant — `pricePercentageLimit`:**

If `pricePercentageLimit > 0`, a non-manager caller is reverted when `newRsETHPrice` exceeds `highestRsethPrice` by more than the limit. However:

1. If `pricePercentageLimit == 0` (its default/unset value), there is no protection at all.
2. Even when set, a stale price that inflates TVL by an amount within the configured limit will pass the check and mint fees against phantom yield.
3. The fee is computed and the rsETH is minted before the price-threshold revert path is reached, so only large stale-price spikes are blocked. [6](#0-5) 

**`updateRSETHPrice()` is permissionless:**

```solidity
// contracts/LRTOracle.sol  line 87
function updateRSETHPrice() public whenNotPaused {
``` [7](#0-6) 

Any EOA can trigger the fee-minting path at will.

---

### Impact Explanation

When a Chainlink feed for a supported LST is stale and the asset's true ETH value has fallen below the last reported price, calling `updateRSETHPrice()` causes the protocol to mint rsETH to the treasury against TVL that does not exist. Every existing rsETH holder's share of the underlying ETH is permanently diluted. This is a direct theft of unclaimed yield from rsETH holders, matching the **High — Theft of unclaimed yield** impact scope.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 h for many LST/ETH feeds). Network congestion, Chainlink node issues, or a feed being deprecated can cause staleness. The attack requires no special role, no front-running, and no capital — only the ability to call a public function. The precondition (a stale feed while the asset's true price has declined) is a realistic, non-negligible operational scenario.

---

### Recommendation

Add a configurable `MAX_STALENESS` constant and validate both `updatedAt` and `answeredInRound` in `ChainlinkPriceOracle.getAssetPrice`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt >= block.timestamp - MAX_STALENESS, "Price too old");
require(price > 0, "Invalid price");
```

---

### Proof of Concept

```solidity
// Foundry test (local, no mainnet)
contract StalePriceTest is Test {
    // Deploy minimal protocol stack with a mock Chainlink feed
    MockChainlinkFeed feed;
    ChainlinkPriceOracle oracle;
    LRTOracle lrtOracle;
    // ... setup omitted for brevity

    function test_staleOraclePhantomFee() public {
        // 1. Set feed price to 1.05e18 (LST at 1.05 ETH), updatedAt = block.timestamp - 48 hours
        feed.setAnswer(1.05e18, block.timestamp - 48 hours);

        // 2. Advance time so the price is now stale; true market price has dropped to 1.00e18
        //    but the feed has NOT been updated

        // 3. Record treasury rsETH balance before
        uint256 treasuryBefore = rsETH.balanceOf(treasury);

        // 4. Anyone calls updateRSETHPrice
        lrtOracle.updateRSETHPrice();

        // 5. Treasury received rsETH despite no real yield
        assertGt(rsETH.balanceOf(treasury), treasuryBefore);
    }
}
```

The mock feed returns a stale inflated price; `_getTotalEthInProtocol` overstates TVL; `rewardAmount > 0`; fee is minted. No real yield accrued.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-32)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

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

**File:** contracts/LRTOracle.sol (L244-247)
```text
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
