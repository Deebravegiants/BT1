### Title
Stale `rsETHPrice` in `instantWithdrawal()` Allows Extraction of Excess Assets Before Oracle Update — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public function that atomically updates the stored `rsETHPrice`. Between a real TVL decrease (e.g., EigenLayer slashing) and the next oracle update, the stored price is stale (higher than actual). `instantWithdrawal()` uses this stale price to compute the asset payout, allowing any rsETH holder to extract more assets than they are entitled to. The resulting loss is then socialized among remaining rsETH holders when the oracle is eventually updated.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a state variable updated only when `updateRSETHPrice()` is explicitly called:

```solidity
// LRTOracle.sol
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

This function is **public** and callable by anyone. It computes the new price from the live on-chain TVL:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

When actual TVL decreases (e.g., EigenLayer slashing reduces `getEffectivePodShares()` or `getAssetBalance()`), the stored `rsETHPrice` becomes stale — it remains at the pre-loss value until `updateRSETHPrice()` is called.

`instantWithdrawal()` computes the payout using the **stored** (stale) price:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
// getExpectedAssetAmount: amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)
```

There is no `min(expectedAmount, currentReturn)` guard as exists in the regular `_calculatePayoutAmount()` path. The attacker burns rsETH and receives assets computed at the inflated stale price, extracting more than their proportional share of the protocol's actual assets.

When `updateRSETHPrice()` is subsequently called, the price drops to reflect the real TVL, and the shortfall is borne by all remaining rsETH holders.

---

### Impact Explanation

**High — Theft of unclaimed yield / proportional assets from other rsETH holders.**

An attacker who holds rsETH can observe that the actual TVL has decreased (by reading EigenLayer state on-chain) before the oracle is updated, then call `instantWithdrawal()` at the stale higher price. They receive `rsETHUnstaked * stalePriceHigh / assetPrice` assets instead of the correct `rsETHUnstaked * actualPriceLow / assetPrice`. The difference is extracted from the pool of assets backing remaining rsETH holders, who receive less when the oracle is updated.

---

### Likelihood Explanation

**Medium.** The attack window exists whenever actual TVL decreases before `updateRSETHPrice()` is called. EigenLayer slashing events are observable on-chain. The attacker does not need to front-run any specific transaction — they only need to act in the window between the TVL decrease and the oracle update. `instantWithdrawal()` must be enabled for the target asset (a manager-controlled flag), which is a prerequisite but not an unlikely one in normal operation.

---

### Recommendation

1. **Call `updateRSETHPrice()` atomically inside `instantWithdrawal()`** before computing `assetAmountUnlocked`, so the price is always fresh at execution time.
2. Alternatively, apply the same `min(expectedAmount, currentReturn)` guard used in `_calculatePayoutAmount()` to `instantWithdrawal()`, computing `currentReturn` from live TVL rather than the stored price.
3. Consider requiring `updateRSETHPrice()` to have been called within a recent time window (e.g., last N blocks) before any withdrawal is processed.

---

### Proof of Concept

1. EigenLayer slashing event reduces `getEffectivePodShares()` for a NodeDelegator. Actual TVL drops by X ETH. Stored `rsETHPrice` is still the pre-slash value `P_high`.

2. Attacker observes the on-chain state change. `updateRSETHPrice()` has not yet been called.

3. Attacker calls `instantWithdrawal(asset, rsETHAmount, "")`:
   - `assetAmountUnlocked = rsETHAmount * P_high / assetPrice` ← uses stale price
   - rsETH is burned; attacker receives `assetAmountUnlocked` assets from `LRTUnstakingVault`

4. Anyone calls `updateRSETHPrice()`. New price `P_low = (TVL - X) / rsethSupply` is stored.

5. Remaining rsETH holders now hold rsETH backed by fewer assets per token. The attacker's excess extraction `rsETHAmount * (P_high - P_low) / assetPrice` is a direct loss to them.

**Key code references:**

`updateRSETHPrice()` is public with no access control: [1](#0-0) 

`instantWithdrawal()` uses stored price without freshness check: [2](#0-1) 

`getExpectedAssetAmount()` reads the stored `rsETHPrice` directly: [3](#0-2) 

The regular withdrawal path applies a `min()` guard that `instantWithdrawal()` lacks: [4](#0-3) 

`_updateRsETHPrice()` computes price from live TVL — the gap between this and the stored value is the exploitable window: [5](#0-4)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
