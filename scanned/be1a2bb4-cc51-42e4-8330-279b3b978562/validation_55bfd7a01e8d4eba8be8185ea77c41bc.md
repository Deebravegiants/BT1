### Title
Stale `rsETHPrice` Used in Deposit and Withdrawal Flows Because `updateRSETHPrice()` Is Never Called Atomically - (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a cached state variable updated only when `updateRSETHPrice()` is explicitly called. Neither `LRTDepositPool.depositAsset()`/`depositETH()` nor `LRTWithdrawalManager.instantWithdrawal()` call `updateRSETHPrice()` before reading `rsETHPrice`. An unprivileged user can exploit the gap between the stale cached price and the real current price to receive more rsETH than deserved on deposit (diluting existing holders), or more underlying assets than deserved on instant withdrawal.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the public state variable `rsETHPrice`: [1](#0-0) 

This value is only updated when `updateRSETHPrice()` is explicitly called: [2](#0-1) 

`updateRSETHPrice()` is `public` and callable by anyone, but it is **never called atomically** inside the deposit or withdrawal execution paths.

**Deposit path:** `LRTDepositPool.getRsETHAmountToMint()` computes the rsETH to mint using the stale cached `rsETHPrice`: [3](#0-2) 

This is called from `_beforeDeposit()`, which is invoked by both `depositAsset()` and `depositETH()`: [4](#0-3) 

**Instant withdrawal path:** `LRTWithdrawalManager.getExpectedAssetAmount()` similarly reads the stale `rsETHPrice` directly: [5](#0-4) 

This is called inside `instantWithdrawal()` to determine how many underlying assets to send the user: [6](#0-5) 

---

### Impact Explanation

**Deposit exploit (theft of yield — High):** As staking rewards accrue, the real rsETH price rises (TVL grows, supply is unchanged). If `updateRSETHPrice()` has not been called recently, `rsETHPrice` is stale and lower than the true value. Because `rsethAmountToMint = amount * assetPrice / rsETHPrice`, a lower denominator yields more rsETH. The attacker receives more rsETH than their deposit warrants, diluting all existing rsETH holders and stealing their accrued yield.

**Instant withdrawal exploit (direct fund theft — Critical):** If `rsETHPrice` is stale and higher than the current real price (e.g., after a slashing event that has not yet been reflected), `getExpectedAssetAmount = rsETHUnstaked * rsETHPrice / assetPrice` returns more underlying assets than the rsETH is actually worth. The attacker burns rsETH and receives excess assets from the unstaking vault.

---

### Likelihood Explanation

`updateRSETHPrice()` is not called by any keeper or bot mentioned in the protocol documentation. The function is `public` and permissionless, meaning any user can choose to call it or not. A rational attacker will simply omit the call when the stale price is favorable to them. The window of staleness grows with every block that passes without a price update, and staking rewards accrue continuously, making the deposit vector reliably exploitable over time.

---

### Recommendation

Call `updateRSETHPrice()` atomically at the start of `depositAsset()`, `depositETH()`, and `instantWithdrawal()` before any price-dependent computation:

```solidity
// In LRTDepositPool.depositAsset() and depositETH():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

// In LRTWithdrawalManager.instantWithdrawal():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
```

Alternatively, replace the cached `rsETHPrice` storage variable with an on-the-fly computation inside `_updateRsETHPrice()` exposed as a `view` function, so callers always receive the live price.

---

### Proof of Concept

1. Staking rewards accrue over time; the real rsETH/ETH rate rises from `1.00 ETH` to `1.05 ETH`, but `updateRSETHPrice()` has not been called, so `rsETHPrice` remains `1.00 ETH`.
2. Attacker calls `LRTDepositPool.depositETH{value: 10 ETH}(minRSETH, "")` **without** first calling `updateRSETHPrice()`.
3. `getRsETHAmountToMint` computes: `10e18 * 1e18 / 1.00e18 = 10 rsETH`. The correct amount at the real price would be `10e18 * 1e18 / 1.05e18 ≈ 9.52 rsETH`.
4. Attacker receives `~0.48 rsETH` more than deserved, extracted from the yield belonging to existing holders.
5. Attacker then calls `updateRSETHPrice()` (or waits for someone else to), and the price updates to `1.05 ETH`. The attacker's rsETH is now worth `10.5 ETH` — a risk-free profit of `~0.48 ETH` at the expense of other depositors.

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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-665)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L228-228)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
