### Title
Stale Chainlink Price Enables Phantom Fee Minting via Block Stuffing — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` timestamp, performing no staleness check. An attacker who stuffs blocks to delay Chainlink keeper updates can then call the public `updateRSETHPrice()` with a stale-high asset price, causing `_getTotalEthInProtocol()` to overstate TVL, triggering fee minting on phantom yield, and diluting existing rsETH holders.

---

### Finding Description

**Root cause — no staleness validation in `ChainlinkPriceOracle.getAssetPrice()`:**

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol line 52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract silently discards `updatedAt` and `answeredInRound`, so it will return the last recorded price regardless of how old it is. [1](#0-0) 

**Fee minting path in `_updateRsETHPrice()`:**

`_getTotalEthInProtocol()` multiplies each asset's total deposit amount by the (potentially stale) oracle price: [2](#0-1) 

The result feeds directly into the fee computation:

```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);   // uses last stored price
// ...
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
``` [3](#0-2) 

If the oracle returns a stale-high price, `totalETHInProtocol` is inflated, `rewardAmount` is phantom, and `protocolFeeInETH` is computed on non-existent yield. The resulting rsETH is minted to treasury: [4](#0-3) 

**`updateRSETHPrice()` is permissionless:** [5](#0-4) 

Any EOA can trigger the fee mint once the oracle is stale.

---

### Impact Explanation

Excess rsETH is minted to the treasury on phantom TVL growth. Because rsETH total supply increases without a corresponding increase in underlying ETH, the NAV per rsETH decreases, diluting all existing holders. The invariant "protocol fee is only minted on genuine yield" is broken.

---

### Likelihood Explanation

**Partial mitigation — `pricePercentageLimit`:**

Lines 252–266 revert if `newRsETHPrice > highestRsethPrice` by more than `pricePercentageLimit`. However:
- If `pricePercentageLimit == 0` (the guard is explicitly disabled), the check is skipped entirely.
- If the stale price inflates the rsETH price by an amount *within* the configured limit (e.g., 0.3% when the limit is 1%), the transaction succeeds and the fee is minted. [6](#0-5) 

**Partial mitigation — `maxFeeMintAmountPerDay`:**

Caps total daily fee minting but does not prevent the phantom fee from being minted up to that cap. [7](#0-6) 

**Block stuffing cost:** On Ethereum mainnet, filling blocks is expensive but feasible when the protocol holds significant TVL. The attacker only needs to delay a single Chainlink heartbeat update (typically 1 hour for ETH-denominated feeds), then call `updateRSETHPrice()` once.

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
require(price > 0, "Non-positive price");
```

`MAX_STALENESS` should be set per feed based on its documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed, with a small buffer).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Deploy with a mock Chainlink feed that returns a fixed stale-high price.
// 1. Set up LRTOracle with ChainlinkPriceOracle pointing to MockFeed.
// 2. Deposit assets so rsethSupply > 0 and rsETHPrice is set to 1e18.
// 3. Configure MockFeed to return price = 1.005e18 (0.5% above current,
//    within a 1% pricePercentageLimit), with updatedAt = block.timestamp - 2 hours.
// 4. Call updateRSETHPrice() as any EOA.
// 5. Assert FeeMinted event was emitted with amount > 0.
// 6. Assert rsETH.totalSupply() increased by rsethAmountToMintAsProtocolFee
//    without any real ETH yield having accrued.

contract MockStaleFeed {
    int256 public price;
    uint256 public updatedAt;

    constructor(int256 _price, uint256 _updatedAt) {
        price = _price;
        updatedAt = _updatedAt;
    }

    function decimals() external pure returns (uint8) { return 18; }

    function latestRoundData() external view returns (
        uint80, int256, uint256, uint256, uint80
    ) {
        // Stale: updatedAt is 2 hours ago, but no staleness check exists
        return (1, price, 0, updatedAt, 1);
    }
}
```

With `MockStaleFeed` returning a price 0.5% above the last stored rsETH price and `updatedAt` two hours in the past, calling `updateRSETHPrice()` succeeds and emits `FeeMinted` with a non-zero amount, proving phantom fee minting on stale oracle data.

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

**File:** contracts/LRTOracle.sol (L205-209)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
```

**File:** contracts/LRTOracle.sol (L234-247)
```text
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
