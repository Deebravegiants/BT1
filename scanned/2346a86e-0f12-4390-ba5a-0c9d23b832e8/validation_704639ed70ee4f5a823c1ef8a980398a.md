### Title
Stale `rsETHPrice` Mixed with Live Asset Price in Mint/Withdrawal Calculations Enables Yield Theft — (File: `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()` each combine two data sources from different states in the same calculation: a **live** Chainlink asset price and a **stale** stored `rsETHPrice`. The rsETH price is only updated when `updateRSETHPrice()` is explicitly called, while asset prices are always fetched live from Chainlink. This is the direct analog of the CometBFT mismatch: data from a previous state is used alongside data from the current state in the same arithmetic, producing inaccurate share/asset amounts.

---

### Finding Description

`LRTDepositPool.getRsETHAmountToMint()` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

- `lrtOracle.getAssetPrice(asset)` calls through `ChainlinkPriceOracle.getAssetPrice()`, which reads `latestRoundData()` from Chainlink — a **live, current-block value**. [2](#0-1) 

- `lrtOracle.rsETHPrice()` returns the **stored** value last written by `_updateRsETHPrice()` — a **stale value from a previous block/state**. [3](#0-2) 

The same mismatch appears in `LRTWithdrawalManager.getExpectedAssetAmount()`:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

`rsETHPrice` is only updated when `updateRSETHPrice()` is called: [5](#0-4) 

This call is not atomic with deposits or withdrawals. Between calls, staking rewards accrue, making the true rsETH price higher than the stored stale value. The two data sources — live asset price and stale rsETH price — are from different protocol states, exactly mirroring the CometBFT height mismatch.

Additionally, `updateRSETHPrice()` reverts for non-managers when the price increase exceeds `pricePercentageLimit`, extending the staleness window: [6](#0-5) 

---

### Impact Explanation

When staking rewards have accrued and the true rsETH price is higher than the stored stale value, a depositor calling `depositAsset()` or `depositETH()` receives:

```
rsethAmountToMint = (depositedETH × liveAssetPrice) / staleRsETHPrice
```

Since `staleRsETHPrice < trueRsETHPrice`, the depositor receives **more rsETH than their deposit is worth at the true price**. This dilutes all existing rsETH holders: when `updateRSETHPrice()` is eventually called, the new price is lower than it would have been without the dilution, and existing holders receive less ETH per rsETH upon withdrawal. This constitutes **theft of unclaimed yield** from existing rsETH holders — **High impact** per the allowed scope.

---

### Likelihood Explanation

This condition is continuously present. Staking rewards accrue every block. `updateRSETHPrice()` is not called atomically with deposits; it is called periodically by off-chain bots or manually. Any deposit made in the interval between reward accrual and the next price update exploits the mismatch. The window is extended when `pricePercentageLimit` blocks non-manager updates, which is the intended behavior for large reward events — precisely the moments when the mismatch is most profitable to exploit.

---

### Recommendation

Compute the rsETH price on-the-fly within `getRsETHAmountToMint` and `getExpectedAssetAmount` using the current TVL and current rsETH supply, rather than reading the stale stored `rsETHPrice`. Alternatively, require that `updateRSETHPrice()` is called atomically before any deposit or withdrawal that uses `rsETHPrice` in its calculation, ensuring both data sources are from the same state.

---

### Proof of Concept

1. Protocol state: 1000 rsETH outstanding, stored `rsETHPrice = 1.0 ETH`, true TVL = 1100 ETH (100 ETH rewards accrued, price not yet updated).
2. `pricePercentageLimit` is set to 5% (1e16 × 5). The true price increase is 10%, so `updateRSETHPrice()` reverts for non-managers.
3. Attacker calls `depositETH{value: 110 ETH}(0, "")`. `getRsETHAmountToMint` computes: `110e18 × 1e18 / 1e18 = 110 rsETH` (at stale price 1.0). At the true price of 1.1, the attacker should receive only 100 rsETH.
4. Manager calls `updateRSETHPriceAsManager()`. New TVL = 1210 ETH, new supply = 1110 rsETH. New price = 1210/1110 ≈ 1.09 ETH/rsETH (diluted from the true 1.1).
5. Attacker holds 110 rsETH × 1.09 = 119.9 ETH value on a 110 ETH deposit — a 9.9 ETH gain extracted from existing holders who earned those rewards. [7](#0-6) [5](#0-4) [6](#0-5)

### Citations

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

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
