Looking at the key contracts to assess this vulnerability claim.

### Title
`SfrxETHPriceOracle` Returns frxETH/sfrxETH Instead of ETH/sfrxETH, Overvaluing sfrxETH Collateral When frxETH Depegs — (`contracts/oracles/SfrxETHPriceOracle.sol`)

---

### Summary

`SfrxETHPriceOracle.getAssetPrice()` returns `sfrxETH.pricePerShare()`, which is denominated in **frxETH per sfrxETH** (not ETH per sfrxETH). The protocol uses this value directly as an ETH exchange rate. When frxETH trades below ETH parity, sfrxETH collateral is systematically overvalued, inflating `rsETHPrice` and allowing sfrxETH depositors to mint excess rsETH at the expense of existing holders.

---

### Finding Description

`SfrxETHPriceOracle.getAssetPrice()` delegates entirely to `sfrxETH.pricePerShare()`: [1](#0-0) 

The interface comment is self-contradictory: it correctly states the return unit is frxETH ("How much frxETH is 1E18 sfrxETH worth") but then incorrectly asserts "Price is in ETH, not USD": [2](#0-1) 

sfrxETH is an ERC-4626 vault whose underlying asset is **frxETH**, not ETH. `pricePerShare()` returns frxETH per sfrxETH. frxETH is a separate token that can and does trade at a discount to ETH on secondary markets.

This value flows into `_getTotalEthInProtocol()` without any frxETH/ETH conversion: [3](#0-2) 

`rsETHPrice` is then computed from this inflated total: [4](#0-3) 

And rsETH minting uses both the inflated asset price and the inflated rsETHPrice: [5](#0-4) 

---

### Impact Explanation

Consider a mixed protocol with 50 ETH and 50 sfrxETH, where `pricePerShare() = 1.05e18` and frxETH trades at 0.99 ETH:

| | Oracle (inflated) | True |
|---|---|---|
| sfrxETH ETH value | 1.05 | 1.0395 |
| totalETHInProtocol | 102.5 | 101.975 |
| rsETHPrice (100 supply) | 1.025 | 1.01975 |

A new depositor of 1 sfrxETH receives:
- **Oracle path**: `1 × 1.05 / 1.025 = 1.0244 rsETH`
- **True fair value**: `1.0395 / 1.01975 = 1.0194 rsETH`
- **Excess**: +0.005 rsETH per sfrxETH deposited

A new depositor of 1 ETH receives:
- **Oracle path**: `1 × 1e18 / 1.025e18 = 0.9756 rsETH`
- **True fair value**: `1 / 1.01975 = 0.9806 rsETH`
- **Shortfall**: −0.005 rsETH per ETH deposited

The excess rsETH minted to sfrxETH depositors dilutes all existing rsETH holders, effectively transferring their accrued yield to the sfrxETH depositor. The magnitude scales with the frxETH/ETH depeg and the proportion of sfrxETH TVL.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- sfrxETH is a named supported asset in the protocol (`SFRX_ETH_TOKEN` in `LRTConstants`). [6](#0-5) 

- The `SfrxETHPriceOracle` is deployed on mainnet at `0x8546A7C8C3C537914C3De24811070334568eF427`.
- frxETH has historically maintained a tight peg but has traded at discounts (e.g., during market stress). The depeg does not need to be large — even a 0.5% discount produces measurable yield theft at scale.
- The exploit path is fully permissionless: any user can call `depositAsset(sfrxETH, ...)` during a frxETH depeg event.
- No admin compromise, front-running, or governance capture is required.

**Likelihood: Medium** (requires frxETH to depeg, which is an external market condition, but the oracle design flaw is always present and the depeg has occurred historically).

---

### Recommendation

Compose `pricePerShare()` with a Chainlink frxETH/ETH price feed to produce a true ETH-denominated rate:

```solidity
// pseudocode
uint256 frxEthPerSfrxEth = ISfrxETH(sfrxETHContractAddress).pricePerShare();
uint256 ethPerFrxEth = IChainlinkFeed(frxEthEthFeed).latestAnswer(); // 1e18-normalized
return frxEthPerSfrxEth.mulWad(ethPerFrxEth);
```

This mirrors how `ChainlinkPriceOracle` handles other assets and eliminates the implicit frxETH ≈ ETH assumption. [7](#0-6) 

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test (Foundry) — run against mainnet fork
// forge test --fork-url $ETH_RPC_URL --match-test testSfrxETHOracleOvervaluation -vvv

import "forge-std/Test.sol";

interface ISfrxETH {
    function pricePerShare() external view returns (uint256);
}

interface IChainlink {
    function latestRoundData() external view returns (
        uint80, int256, uint256, uint256, uint80
    );
    function decimals() external view returns (uint8);
}

contract SfrxETHOraclePoC is Test {
    // Mainnet addresses
    address constant SFRXETH = 0xac3E018457B222d93114458476f3E3416Abbe38F;
    // Chainlink frxETH/ETH feed (if available) or use frxETH/USD + ETH/USD
    // For demonstration, we simulate a 1% frxETH depeg

    function testSfrxETHOracleOvervaluation() public {
        uint256 pricePerShare = ISfrxETH(SFRXETH).pricePerShare();

        // Oracle reports this as ETH/sfrxETH
        uint256 oracleReportedEthValue = pricePerShare;

        // Simulate frxETH trading at 0.99 ETH (1% depeg)
        uint256 frxEthToEth = 0.99e18;
        uint256 trueEthValue = pricePerShare * frxEthToEth / 1e18;

        uint256 overvaluation = oracleReportedEthValue - trueEthValue;
        uint256 overvaluationBps = overvaluation * 10_000 / trueEthValue;

        emit log_named_uint("Oracle ETH/sfrxETH (frxETH treated as ETH)", oracleReportedEthValue);
        emit log_named_uint("True ETH/sfrxETH", trueEthValue);
        emit log_named_uint("Overvaluation (bps)", overvaluationBps); // ~100 bps = 1%

        // Assert overvaluation is non-zero when frxETH depegs
        assertGt(overvaluation, 0, "No overvaluation when frxETH depegs");

        // With 10,000 sfrxETH in protocol, overstatement of totalETHInProtocol:
        uint256 totalSfrxETH = 10_000e18;
        uint256 overstatedTVL = totalSfrxETH * overvaluation / 1e18;
        emit log_named_uint("Overstated TVL (ETH) for 10k sfrxETH", overstatedTVL);
        // ~105 ETH overstated — directly inflates rsETHPrice and enables yield theft
    }
}
```

### Citations

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L8-11)
```text
interface ISfrxETH {
    /// @notice How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD
    function pricePerShare() external view returns (uint256);
}
```

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L35-41)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != sfrxETHContractAddress) {
            revert InvalidAsset();
        }

        return ISfrxETH(sfrxETHContractAddress).pricePerShare();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/utils/LRTConstants.sol (L10-10)
```text
    bytes32 public constant SFRX_ETH_TOKEN = keccak256("SFRX_ETH_TOKEN");
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```
