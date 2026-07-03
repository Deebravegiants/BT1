### Title
`assetsCommitted` Desync Allows Over-Commitment of Withdrawal Requests When rsETH Depreciates - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
In `LRTWithdrawalManager`, when `unlockQueue` processes requests after rsETH has depreciated relative to the underlying asset, `assetsCommitted[asset]` is decremented by the original committed amount (`request.expectedAssetAmount`) rather than the actual payout amount (`payoutAmount`). This creates phantom "available" capacity in `getAvailableAssetAmount`, allowing new withdrawal requests to be created for assets that do not exist in the protocol, rendering those new requests unsatisfiable.

### Finding Description

The desynchronization occurs across two functions:

**`initiateWithdrawal`** (lines 150–178) atomically transfers rsETH and increments `assetsCommitted`:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked); // line 166
assetsCommitted[asset] += expectedAssetAmount;                                         // line 173
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);                  // line 175
```

**`_unlockWithdrawalRequests`** (lines 770–816) decrements `assetsCommitted` by the **original** committed amount, but only redeems the **actual** payout:

```solidity
assetsCommitted[asset] -= request.expectedAssetAmount;  // line 802 — decrements by ORIGINAL amount
request.expectedAssetAmount = payoutAmount;             // line 804 — updates to ACTUAL payout
assetAmountToUnlock += payoutAmount;                    // line 807 — only this is redeemed from vault
```

`payoutAmount` is computed by `_calculatePayoutAmount` (lines 824–835):

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

When rsETH has depreciated relative to the asset (e.g., due to slashing), `currentReturn < request.expectedAssetAmount`, so `payoutAmount < request.expectedAssetAmount`.

**The desync**: `assetsCommitted` is decremented by `expectedAssetAmount` (larger), but the vault only redeems `payoutAmount` (smaller). The gap `expectedAssetAmount − payoutAmount` is phantom capacity that does not correspond to any real assets.

`getAvailableAssetAmount` (lines 599–603) uses:

```solidity
uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
```

After `unlockQueue`:
- `totalAssets` decreases by `payoutAmount` (assets leave the vault)
- `assetsCommitted` decreases by `expectedAssetAmount` (> `payoutAmount`)
- Net: `getAvailableAssetAmount` increases by `expectedAssetAmount − payoutAmount` — phantom capacity

Any user calling `initiateWithdrawal` after this point can create a withdrawal request backed by this phantom capacity. When that request is later processed by `unlockQueue`, the vault will not have sufficient assets to satisfy it, causing the request to be permanently skipped or stuck.

### Impact Explanation

**Temporary (potentially permanent) freezing of funds.** Users who create withdrawal requests during the phantom-capacity window will have their rsETH locked in the contract (transferred in at line 166) with no corresponding assets available to satisfy their request. Their rsETH is held by the contract but cannot be redeemed, and there is no cancellation mechanism visible in the contract.

### Likelihood Explanation

**Medium.** rsETH depreciation relative to an underlying LST is a realistic and expected scenario (EigenLayer slashing, LST depeg). Every time `unlockQueue` is called after such a depreciation event, the phantom capacity is created. Any user who calls `initiateWithdrawal` in the window between `unlockQueue` and the next asset replenishment will be affected.

### Recommendation

Decrement `assetsCommitted` by `payoutAmount` (the actual amount leaving the protocol) rather than `request.expectedAssetAmount` (the original committed amount):

```solidity
// In _unlockWithdrawalRequests, replace line 802:
assetsCommitted[asset] -= payoutAmount;  // was: request.expectedAssetAmount
request.expectedAssetAmount = payoutAmount;
```

This ensures `assetsCommitted` accurately reflects the assets still owed to pending requests, preventing phantom capacity from appearing in `getAvailableAssetAmount`.

### Proof of Concept

1. Protocol has 100 ETHx in the vault. rsETH/ETHx rate = 1:1.
2. User A calls `initiateWithdrawal(ETHx, 100 rsETH)`:
   - `assetsCommitted[ETHx] += 100` → `assetsCommitted = 100`
   - Request stored: `expectedAssetAmount = 100`
3. rsETH depreciates: rsETH/ETHx rate drops to 0.9 (e.g., slashing).
4. Operator calls `unlockQueue(ETHx, ...)`:
   - `payoutAmount = min(100, 90) = 90`
   - `assetsCommitted[ETHx] -= 100` → `assetsCommitted = 0` ← **decremented by original, not payout**
   - Vault redeems 90 ETHx → vault now has 10 ETHx remaining
5. `getAvailableAssetAmount(ETHx)`:
   - `totalAssets = 10` (vault has 10 remaining)
   - `assetsCommitted = 0`
   - Returns `10` — **phantom capacity** (these 10 ETHx are not actually free; they are residual from the vault but `assetsCommitted` was over-decremented)
6. User B calls `initiateWithdrawal(ETHx, 11 rsETH)` — passes the availability check (10 ETHx available per accounting).
   - `assetsCommitted[ETHx] += 9.9` (≈10 at current rate)
   - rsETH transferred from User B to contract
7. Operator calls `unlockQueue` for User B's request: vault only has 10 ETHx but User B's request needs ~9.9 ETHx. If the vault is drained by other operations in the interim, User B's request cannot be unlocked.
8. User B's rsETH is locked in `LRTWithdrawalManager` with no path to completion. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
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

**File:** contracts/LRTWithdrawalManager.sol (L800-808)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
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
    }
```
