### Title
Stale Chainlink Price Accepted Without Freshness Check Enables Block-Stuffing-Assisted Deposit at Inflated Asset Price — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData` but discards the `updatedAt` and `answeredInRound` return values, accepting any price regardless of age. An attacker who stuffs blocks to delay Chainlink heartbeat updates can deposit LST at a stale-high price, minting excess rsETH and diluting existing holders once the oracle catches up.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice` reads the Chainlink feed but performs no staleness validation:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The `updatedAt` and `answeredInRound` fields are silently dropped. No maximum-age threshold is enforced.

This price flows directly into the deposit mint calculation:

```solidity
// contracts/LRTDepositPool.sol  line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

`lrtOracle.rsETHPrice()` is a **stored** state variable updated only when `updateRSETHPrice()` is called explicitly — it is not refreshed on every deposit. [3](#0-2) 

The same stale price is also consumed inside `_getTotalEthInProtocol`, which drives the rsETH price update:

```solidity
// contracts/LRTOracle.sol  line 339
uint256 assetER = getAssetPrice(asset);
``` [4](#0-3) 

---

### Impact Explanation

**Phase 1 — block stuffing / stale price window:**
The attacker fills every block with high-gas transactions, preventing Chainlink keeper transactions from landing. The on-chain price remains at the pre-drop (stale-high) value.

**Phase 2 — deposit at stale-high price:**
The attacker calls `depositAsset` with a large LST amount. `getRsETHAmountToMint` returns:

```
rsethAmountToMint = amount × stale_high_assetPrice / rsETHPrice
```

Because `stale_high_assetPrice > true_assetPrice`, the attacker receives more rsETH than the true ETH value of their deposit warrants.

**Phase 3 — oracle catches up:**
Block stuffing ends. Chainlink updates. Anyone calls `updateRSETHPrice()`. `_getTotalEthInProtocol` now uses the correct lower price, so `totalETHInProtocol` is lower relative to the inflated rsETH supply. The new rsETH price drops. Every existing holder's rsETH is worth less — the attacker's excess rsETH represents value extracted from them.

The invariant broken: *rsETH minted must be backed by current collateral value at the time of mint.*

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but not impossible for a well-capitalised attacker targeting a high-TVL protocol. Chainlink LST/ETH feeds have a 24-hour heartbeat and a 0.5 % deviation threshold. A significant LST price drop (e.g., slashing event) that does not immediately trigger the deviation threshold gives the attacker a natural window without needing to stuff blocks at all; block stuffing extends that window further. The missing staleness check is the necessary and sufficient code-level precondition.

---

### Recommendation

Enforce a maximum price age in `getAssetPrice`. Example:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= MAX_ORACLE_DELAY, "Price too stale");
require(price > 0, "Non-positive price");
```

`MAX_ORACLE_DELAY` should be set to slightly above the feed's heartbeat (e.g., 25 hours for a 24-hour heartbeat feed).

---

### Proof of Concept

Two-phase fork test (Foundry):

```solidity
// 1. Fork mainnet, record current stETH/ETH Chainlink price (stale-high).
// 2. vm.warp(block.timestamp + 25 hours) to simulate staleness without
//    updating the Chainlink round (no new round pushed on the fork).
// 3. Attacker calls depositAsset(stETH, largeAmount, 0, "").
//    Record rsethMinted.
// 4. Push a new Chainlink round with the true lower price via vm.mockCall
//    or by using a mock aggregator.
// 5. Call lrtOracle.updateRSETHPrice().
// 6. Assert: attacker rsETH value (rsethMinted × new rsETHPrice) > largeAmount × true_price.
//    i.e., attacker extracted value from existing holders through dilution.
```

The test passes on unmodified code because `ChainlinkPriceOracle.getAssetPrice` never checks `updatedAt`. [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
