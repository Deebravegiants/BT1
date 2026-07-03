### Title
`assetsCommitted` Decremented by Original Amount While Only `payoutAmount` Is Redeemed, Inflating `getAvailableAssetAmount` and Enabling Over-Commitment of Withdrawal Requests - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`_unlockWithdrawalRequests` decrements `assetsCommitted[asset]` by the original `request.expectedAssetAmount` but only redeems `payoutAmount` (which can be strictly less) from the unstaking vault. Because `getAvailableAssetAmount` derives available liquidity from `getTotalAssetDeposits(asset) - assetsCommitted[asset]`, the discrepancy inflates the apparent available amount by `expectedAssetAmount - payoutAmount`. Subsequent callers of `initiateWithdrawal` can commit against this phantom liquidity, queuing withdrawal requests that can never be unlocked and permanently trapping their rsETH in the withdrawal manager until an operator manually replenishes the vault.

---

### Finding Description

**Root cause — `_unlockWithdrawalRequests` (lines 798–815):**

```solidity
uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);
// ...
assetsCommitted[asset] -= request.expectedAssetAmount;   // ← original (larger) amount
request.expectedAssetAmount = payoutAmount;              // ← updated to actual (smaller) amount
```

`_calculatePayoutAmount` returns `min(request.expectedAssetAmount, currentReturn)`. When the rsETH/asset exchange rate has moved unfavourably since initiation, `currentReturn < request.expectedAssetAmount`, so `payoutAmount < request.expectedAssetAmount`.

After `_unlockWithdrawalRequests` returns, `unlockQueue` redeems exactly `assetAmountUnlocked` (the sum of `payoutAmount` values) from the vault:

```solidity
unstakingVault.redeem(asset, assetAmountUnlocked);   // line 307
```

So the vault loses `payoutAmount`, but `assetsCommitted` was reduced by `expectedAssetAmount`. The net effect on `getAvailableAssetAmount`:

```
getAvailableAssetAmount
  = getTotalAssetDeposits(asset) - assetsCommitted[asset]
```

`getTotalAssetDeposits` includes `assetLyingUnstakingVault` (vault balance) but **not** assets sitting in the withdrawal manager. After unlock:

- `assetLyingUnstakingVault` decreases by `payoutAmount`
- `assetsCommitted` decreases by `expectedAssetAmount`

Net change to `getAvailableAssetAmount` = `+(expectedAssetAmount − payoutAmount)` — phantom liquidity.

**Over-commitment path — `initiateWithdrawal` (lines 168–173):**

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
```

Any unprivileged user can call `initiateWithdrawal` and pass the guard using the inflated `getAvailableAssetAmount`. Their rsETH is transferred to the contract, but the corresponding assets do not exist in the vault. When `unlockQueue` later runs, `unstakingVault.balanceOf(asset)` is insufficient to cover the phantom request, so the loop exits early and the request remains permanently locked.

---

### Impact Explanation

Users whose withdrawal requests are backed by phantom liquidity have their rsETH transferred into `LRTWithdrawalManager` and cannot retrieve it until an operator manually tops up the unstaking vault. This constitutes a **temporary freeze of user funds** (Medium severity). The magnitude of the phantom amount equals the cumulative price-drift discount across all previously unlocked requests, which can be material during volatile market conditions.

---

### Likelihood Explanation

The condition `payoutAmount < expectedAssetAmount` is triggered whenever the rsETH/asset exchange rate moves between a user's `initiateWithdrawal` call and the operator's `unlockQueue` call. Given that the withdrawal delay is configurable up to 16 days and that rsETH/LST prices fluctuate continuously, this condition will occur in normal protocol operation. No privileged access or special setup is required beyond ordinary market price movement.

---

### Recommendation

Track the total asset amount actually redeemed for unlocked requests separately (e.g., `assetsAllocated[asset]`), and subtract it from `getTotalAssetDeposits` in `getAvailableAssetAmount` instead of relying on `assetsCommitted`. Alternatively, decrement `assetsCommitted` by `payoutAmount` rather than `request.expectedAssetAmount` so the accounting reflects the actual vault outflow:

```solidity
assetsCommitted[asset] -= payoutAmount;   // use actual payout, not original committed amount
```

---

### Proof of Concept

**Setup:** 100 ETH in `LRTUnstakingVault`. rsETH price = 1.0 ETH/rsETH. ETH asset price = 1.0.

1. **User A** calls `initiateWithdrawal(ETH, 10 rsETH)`.
   - `expectedAssetAmount = 10 ETH`; `assetsCommitted = 10`
   - `getAvailableAssetAmount = 100 − 10 = 90`

2. rsETH price drops to 0.8 ETH/rsETH (or asset price rises).

3. Operator calls `unlockQueue(ETH, ...)`.
   - `payoutAmount = min(10, 8) = 8 ETH`
   - `assetsCommitted -= 10` → `assetsCommitted = 0`
   - Vault redeems 8 ETH → vault balance = 92 ETH
   - `getAvailableAssetAmount = 92 − 0 = 92` ← **phantom +2 ETH**

4. **User B** calls `initiateWithdrawal(ETH, 92 rsETH)`.
   - `expectedAssetAmount = 92 ETH`; guard passes (92 ≤ 92)
   - `assetsCommitted = 92`; User B's 92 rsETH locked in contract

5. Operator calls `unlockQueue(ETH, ...)`.
   - `unstakingVault.balanceOf(ETH) = 92 ETH`
   - `payoutAmount` for User B's request = 92 ETH (or less if price moved again)
   - Vault is drained; User B's request unlocked only if vault has exactly 92 ETH

6. If any subsequent price drift occurs, or if the vault was already partially drained, User B's request cannot be unlocked. User B's 92 rsETH remains trapped in `LRTWithdrawalManager`.

**Key lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L301-307)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L798-808)
```text
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

```

**File:** contracts/LRTWithdrawalManager.sol (L824-834)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```
