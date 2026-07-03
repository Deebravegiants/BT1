### Title
Stale `rsETHPrice` During `PriceAboveDailyThreshold` Window Enables Over-Minting and Protocol Insolvency - (File: contracts/LRTOracle.sol)

---

### Summary

When the actual rsETH price increases beyond `pricePercentageLimit` (e.g., due to a large EigenLayer or staking reward event), non-manager callers cannot update `rsETHPrice` — the call reverts with `PriceAboveDailyThreshold`. During this window the stale, lower `rsETHPrice` remains in storage and is used verbatim by `LRTDepositPool.getRsETHAmountToMint()`. An unprivileged depositor can mint more rsETH than the actual backing warrants, then redeem at the corrected price after the manager updates it, extracting more ETH than was deposited and leaving the protocol insolvent.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` computes a fresh price and then checks whether the increase exceeds the configured threshold:

```solidity
// contracts/LRTOracle.sol  lines 252-266
if (newRsETHPrice > highestRsethPrice) {
    uint256 priceDifference = newRsETHPrice - highestRsethPrice;
    bool isPriceIncreaseOffLimit =
        pricePercentageLimit > 0 &&
        priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceIncreaseOffLimit) {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
            revert PriceAboveDailyThreshold();   // ← reverts; rsETHPrice NOT updated
        }
    }
}
``` [1](#0-0) 

The revert unwinds the entire call, so `rsETHPrice` (line 313) is never written. The stale, lower value persists in storage until a manager intervenes. [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` reads this stale value directly:

```solidity
// contracts/LRTDepositPool.sol  line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

Because `rsETHPrice` is the denominator, a stale **lower** price produces a **larger** rsETH mint amount. There is no staleness guard, no deposit pause, and no freshness check in `depositETH()` or `depositAsset()`. [4](#0-3) 

Contrast this with the downside-protection path, which **does** pause the protocol when the price drops too far:

```solidity
// contracts/LRTOracle.sol  lines 277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [5](#0-4) 

No equivalent protection exists for the upside case. Deposits continue unimpeded while `rsETHPrice` is stale.

On the withdrawal side, `LRTWithdrawalManager.getExpectedAssetAmount()` also reads `rsETHPrice`:

```solidity
// contracts/LRTWithdrawalManager.sol  line 593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [6](#0-5) 

Once the manager corrects the price upward, the attacker's rsETH — minted cheaply at the stale price — redeems for more ETH than was deposited.

---

### Impact Explanation

**Critical — Protocol insolvency.**

An attacker who deposits `D` ETH while `rsETHPrice = P_stale` receives:

```
rsETH_minted = D * assetPrice / P_stale
```

After the manager updates to `P_actual > P_stale`, the attacker withdraws:

```
ETH_received = rsETH_minted * P_actual / assetPrice
             = D * (P_actual / P_stale)
             > D
```

The surplus `D * (P_actual/P_stale - 1)` is extracted from the pool at the expense of honest depositors. If the price gap is large (e.g., 5 % reward event with a 1 % daily limit), the attacker extracts ~5 % of their deposit as pure profit. Repeated or large-scale exploitation leaves the protocol with more rsETH obligations than backing ETH — the definition of insolvency.

---

### Likelihood Explanation

**Medium.**

- EigenLayer restaking rewards and LST rebases can produce single-period TVL increases that exceed a conservatively set `pricePercentageLimit` (e.g., 1 %).
- `updateRSETHPrice()` is a public, permissionless function; any on-chain observer can detect the moment it starts reverting.
- The manager response window (minutes to hours) is sufficient for a monitoring attacker to deposit and lock in the stale-price rsETH before the correction.
- No special privileges, flash loans, or oracle manipulation are required — only a standard `depositETH()` call.

---

### Recommendation

1. **Mirror the downside protection on the upside:** when `isPriceIncreaseOffLimit` is true, pause `LRTDepositPool` (and optionally `LRTWithdrawalManager`) until a manager resolves the price, exactly as is done for excessive price decreases.

2. **Alternatively**, compute the mint amount from live TVL rather than the cached `rsETHPrice`, so that the denominator always reflects the current backing even when the stored price is stale.

3. **At minimum**, emit a prominent event when `PriceAboveDailyThreshold` is hit so off-chain monitoring can trigger an immediate manager response.

---

### Proof of Concept

1. Protocol is live with `pricePercentageLimit = 1e16` (1 %) and `rsETHPrice = 1.00 ETH`.
2. A large EigenLayer reward batch is processed; actual TVL rises 5 %. The true price is now `1.05 ETH`.
3. Attacker calls `updateRSETHPrice()` → reverts `PriceAboveDailyThreshold`. `rsETHPrice` stays at `1.00 ETH`.
4. Attacker calls `depositETH{value: 1000 ether}(0, "")`.
   - `getRsETHAmountToMint` returns `1000e18 * 1e18 / 1.00e18 = 1000e18` rsETH.
   - Correct amount at true price would be `1000e18 / 1.05e18 ≈ 952.38e18` rsETH.
   - Attacker receives **~47.6 rsETH excess**.
5. Manager calls `updateRSETHPriceAsManager()`. `rsETHPrice` is updated to `1.05 ETH`.
6. Attacker calls `initiateWithdrawal(ETH, 1000e18, "")`.
   - `getExpectedAssetAmount` returns `1000e18 * 1.05e18 / 1e18 = 1050 ETH`.
7. After the delay, attacker receives **1050 ETH** having deposited **1000 ETH** — a 50 ETH profit drawn from the shared pool, leaving the protocol insolvent by that amount.

### Citations

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

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
