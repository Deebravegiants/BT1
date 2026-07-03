### Title
Stale Stored `rsETHPrice` Used in L2 Pool Deposit Minting Allows Depositors to Receive Excess rsETH — (`contracts/cross-chain/RSETHRateProvider.sol`, `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

All L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) compute the rsETH minting amount for depositors by reading `ILRTOracle.rsETHPrice()`, which is a **stored state variable** that is only updated when `updateRSETHPrice()` is explicitly called. No pool deposit path triggers a price update before reading the rate. When the stored price is stale (lower than the true current price), depositors receive more rsETH than they are entitled to, diluting existing holders and stealing accrued yield.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a state variable `rsETHPrice`: [1](#0-0) 

This value is only refreshed when `updateRSETHPrice()` or `updateRSETHPriceAsManager()` is called: [2](#0-1) 

The rate providers consumed by pool contracts read this stored value directly without triggering a refresh: [3](#0-2) [4](#0-3) 

Every L2 pool deposit path calls `viewSwapRsETHAmountAndFee()`, which calls `getRate()`, which calls the rate provider's `getRate()` — returning the stale stored value: [5](#0-4) 

The minting formula is:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

Because rsETH accrues restaking rewards over time, its true price in ETH monotonically increases. If `rsETHPrice` has not been updated since the last reward accrual, it is **lower** than the true current price. A lower denominator yields a **larger** `rsETHAmount`, meaning the depositor receives more rsETH than their ETH contribution warrants.

The same stale value is used in the fee calculation inside `_updateRsETHPrice()`: [6](#0-5) 

A stale (understated) `rsETHPrice` understates `previousTVL`, overstates `rewardAmount`, and therefore overstates the protocol fee minted to treasury — compounding the mis-accounting.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders' accrued restaking yield is represented by the appreciation of `rsETHPrice`. When a depositor mints rsETH at a stale lower price, they receive a larger share of the total rsETH supply than their ETH contribution justifies. This dilutes the per-token ETH backing of all existing holders, effectively transferring accrued yield to the new depositor. The magnitude scales with (a) how long since the last price update and (b) deposit size. In periods of high restaking reward accrual or low update frequency, the loss to existing holders is material.

---

### Likelihood Explanation

`updateRSETHPrice()` is a public function but is not called atomically within any deposit transaction. There is no on-chain enforcement that the price is fresh before minting. Any depositor can observe a stale `rsETHPrice` on-chain (by comparing `rsETHPrice` against a freshly computed value off-chain) and deposit before anyone calls `updateRSETHPrice()`. The window of staleness grows with every block that passes without an update call, and the protocol relies entirely on off-chain keepers or altruistic callers to keep the price current.

---

### Recommendation

Before computing `rsETHAmount` in each pool's deposit path, trigger a price update so the rate used for minting is always current. Concretely, the rate provider (or the pool itself) should call `updateRSETHPrice()` on `LRTOracle` before reading `rsETHPrice()`, analogous to how the BarnBridge fix replaced `exchangeRateStored` with `exchangeRateCurrent` (which accrues interest before returning the rate). Alternatively, expose a `rsETHPriceCurrent()` view on `LRTOracle` that computes the price on-the-fly from live TVL without writing state, and have pool contracts call that instead of the stored `rsETHPrice`.

---

### Proof of Concept

1. At time T, `LRTOracle.rsETHPrice = 1.01e18` (last updated).
2. Restaking rewards accrue; true price rises to `1.02e18`, but `updateRSETHPrice()` has not been called.
3. Attacker calls `RSETHPoolV3.deposit{value: 100 ether}("ref")`.
4. `viewSwapRsETHAmountAndFee(100e18)` → `getRate()` → `RSETHRateProvider.getLatestRate()` → returns stale `1.01e18`.
5. `rsETHAmount = (100e18 - fee) * 1e18 / 1.01e18 ≈ 99.0099 rsETH`.
6. Correct amount at true price: `(100e18 - fee) * 1e18 / 1.02e18 ≈ 98.0392 rsETH`.
7. Attacker receives `≈ 0.97 rsETH` excess — value extracted from existing holders' accrued yield.
8. Attacker can then call `updateRSETHPrice()` themselves after minting to lock in the gain. [3](#0-2) [5](#0-4) [1](#0-0) [2](#0-1)

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

**File:** contracts/LRTOracle.sol (L233-234)
```text
        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L26-28)
```text
    /// @notice Returns the latest rate from the rsETH contract
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
