### Title
Stale Cached `rsETHPrice` Used in Deposit Mint Calculation Enables Yield Theft from Existing rsETH Holders - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTOracle.rsETHPrice` is a manually-updated stored value. `LRTDepositPool.getRsETHAmountToMint` uses this cached price as the denominator when computing how many rsETH tokens to mint for a new deposit. Because rsETH is a yield-bearing token whose true price continuously increases as staking rewards accrue, the cached price is always ≤ the true current price between updates. An unprivileged depositor can exploit this gap to receive more rsETH than fair value, diluting existing holders of their accrued yield.

### Finding Description
`LRTOracle` stores `rsETHPrice` as a state variable updated only when `updateRSETHPrice()` is explicitly called (publicly callable but not automatically triggered on deposits). [1](#0-0) 

`_updateRsETHPrice()` computes the new price from live TVL and rsETH supply, then writes it to storage: [2](#0-1) [3](#0-2) 

`LRTDepositPool.getRsETHAmountToMint` reads the cached `rsETHPrice` directly without triggering an update: [4](#0-3) 

The numerator (`lrtOracle.getAssetPrice(asset)`) is a live Chainlink read, while the denominator (`lrtOracle.rsETHPrice()`) is the stale cached value. As staking rewards accrue between updates, the true rsETH price rises but the denominator stays low, causing the division to yield a larger-than-correct rsETH mint amount.

This is structurally identical to the MagicLpAggregator pattern: a pricing mechanism that always returns a value ≤ the true current value (MagicLpAggregator uses `min(priceA, priceB)` for all reserves; here the cached price lags the true yield-accrued price), enabling an attacker to acquire the token at below-fair-value and profit at the expense of existing holders.

### Impact Explanation
An attacker who deposits assets while `rsETHPrice` is stale receives more rsETH than their deposit is worth at the true current price. After calling `updateRSETHPrice()` (publicly callable), the price corrects upward, and the attacker holds rsETH worth more than what they paid. The delta comes directly from the yield that had accrued to existing rsETH holders but was not yet reflected in the cached price. This is a theft of unclaimed yield from all existing rsETH holders, proportional to the deposit size and the staleness gap.

**Impact: High — Theft of unclaimed yield.**

### Likelihood Explanation
`updateRSETHPrice()` is not called atomically within `depositAsset`. Any time between two consecutive price updates (which can be hours apart in practice, especially during low-activity periods or if keeper bots are delayed), the cached price lags the true value. rsETH accrues staking rewards continuously (~4–5% APY across multiple LSTs), so even a 1-hour staleness window creates a measurable gap. The attack requires no special role, no governance capture, and no external protocol compromise — only a public `depositAsset` call followed by a public `updateRSETHPrice` call.

### Recommendation
Call `_updateRsETHPrice()` (or at minimum read the live computed price) before computing `rsethAmountToMint` inside `getRsETHAmountToMint`. Alternatively, compute the mint amount using a freshly derived price rather than the stored `rsETHPrice` state variable, so that the denominator always reflects the current TVL/supply ratio at the time of deposit.

### Proof of Concept
1. Assume `rsETHPrice` was last updated 6 hours ago at `1.040 ETH`. Since then, staking rewards have accrued and the true price is now `1.041 ETH`.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, ...)`.
3. `getRsETHAmountToMint` computes: `1000e18 * 1e18 / 1.040e18 = 961.538... rsETH` (using stale price).
4. True fair amount: `1000e18 * 1e18 / 1.041e18 = 960.615... rsETH`.
5. Attacker receives `~0.923 rsETH` more than fair value.
6. Attacker calls `updateRSETHPrice()` — price updates to `1.041 ETH`.
7. Attacker's rsETH is now worth `961.538 * 1.041 = 1000.96 ETH` while they deposited `1000 ETH` worth of stETH.
8. The `~0.96 ETH` profit is extracted from the yield that belonged to pre-existing rsETH holders. [4](#0-3) [5](#0-4) [3](#0-2)

### Citations

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
