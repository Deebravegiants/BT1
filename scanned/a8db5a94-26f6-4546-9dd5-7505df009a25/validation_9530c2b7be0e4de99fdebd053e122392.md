### Title
`_calculatePayoutAmount` Caps User Payout at Request-Time Oracle Price, Permanently Stripping Accrued Yield During Withdrawal Delay — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._calculatePayoutAmount` returns `min(expectedAssetAmount, currentReturn)`. Because rsETH appreciates continuously from staking rewards, `currentReturn` at unlock time will routinely exceed `expectedAssetAmount` (locked at request time). The user is capped at the request-time value; the difference stays in the vault as uncommitted assets and is ultimately sweepable to the treasury. Every user who withdraws over the mandatory 8-day delay loses the yield that accrued on their rsETH during that window.

---

### Finding Description

**Withdrawal flow:**

1. `initiateWithdrawal` — user transfers rsETH to the contract; `expectedAssetAmount` is snapshotted from the oracle at that moment; `assetsCommitted[asset] += expectedAssetAmount`.
2. `unlockQueue` (operator-called, after `withdrawalDelayBlocks`) — calls `_calculatePayoutAmount` with the *current* oracle prices and overwrites `request.expectedAssetAmount = payoutAmount`.
3. `completeWithdrawal` — user receives `request.expectedAssetAmount`.

**Root cause — `_calculatePayoutAmount`:**

```solidity
// contracts/LRTWithdrawalManager.sol  line 833-834
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

When rsETH price has risen between request and unlock (the normal case — staking rewards accrue into TVL, raising `rsETHPrice`), `currentReturn > expectedAssetAmount`. The function returns `expectedAssetAmount`, capping the user at the stale request-time value.

**Asset accounting in `_unlockWithdrawalRequests`:**

```solidity
// contracts/LRTWithdrawalManager.sol  line 802-807
assetsCommitted[asset] -= request.expectedAssetAmount;   // full original commitment released
request.expectedAssetAmount = payoutAmount;              // user's record overwritten to the min
...
assetAmountToUnlock += payoutAmount;                     // only payoutAmount leaves the vault
```

`assetsCommitted` is reduced by the full original `expectedAssetAmount`, but only `payoutAmount` (= `expectedAssetAmount` when capped) is taken from the vault. The surplus `currentReturn − expectedAssetAmount` remains in the vault as uncommitted assets, available to be swept to the treasury via `sweepRemainingAssets`.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Every withdrawing user loses the staking yield that accrued on their rsETH during the mandatory withdrawal delay (~8 days). The yield is not returned to the user; it accumulates as uncommitted assets in `LRTUnstakingVault` and is sweepable to the protocol treasury. This is a systematic, per-withdrawal loss of yield for all users, not a one-off edge case.

---

### Likelihood Explanation

**High.** rsETH price increases monotonically under normal protocol operation (staking rewards raise TVL, raising `rsETHPrice`). The default withdrawal delay is `8 days / 12 seconds` blocks. Over any 8-day window, rsETH price will increase by the staking APR fraction (~3–5% annualised ≈ ~0.07–0.11% per 8 days). Every withdrawal request will therefore hit the cap, and every user will lose that fraction of their withdrawal value.

---

### Recommendation

Replace the `min` cap with a `max` (or remove the cap entirely on the upside). The cap was presumably intended to protect users from receiving *less* than expected when rsETH price drops, but it should not penalise users when rsETH price rises. A correct formulation is:

```solidity
// Give user the better of the two: protect against price drops, pass through price gains
return (request.expectedAssetAmount > currentReturn) ? request.expectedAssetAmount : currentReturn;
```

Alternatively, snapshot the rsETH amount and burn it at `completeWithdrawal` time using the then-current price, so the user always receives fair value at the moment of actual settlement.

---

### Proof of Concept

**Setup:**
- rsETH price at request time (T1): `1.050 ETH/rsETH`
- stETH price: `1.000 ETH/stETH`
- User calls `initiateWithdrawal(stETH, 100e18)`:
  - `expectedAssetAmount = 100e18 * 1.050e18 / 1.000e18 = 105e18 stETH`
  - `assetsCommitted[stETH] += 105e18`

**8 days later — staking rewards accrue:**
- rsETH price at unlock time (T2): `1.060 ETH/rsETH` (normal ~3.5% APR over 8 days)
- Operator calls `unlockQueue(stETH, ...)`:
  - `currentReturn = 100e18 * 1.060e18 / 1.000e18 = 106e18 stETH`
  - `_calculatePayoutAmount` returns `min(105e18, 106e18) = 105e18`
  - `assetsCommitted[stETH] -= 105e18` (full commitment released)
  - `assetAmountToUnlock += 105e18` (only 105 stETH leaves vault)
  - `1e18 stETH` remains in vault, uncommitted

**User calls `completeWithdrawal`:**
- Receives `105e18 stETH` instead of the `106e18 stETH` their rsETH was worth at settlement time
- Loss: `1e18 stETH` (~0.95% of withdrawal value) permanently stripped and left for treasury sweep

The loss scales with withdrawal size and delay duration. A user withdrawing 10,000 rsETH over 8 days loses ~10 stETH of yield with no recourse. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-176)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L798-807)
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
