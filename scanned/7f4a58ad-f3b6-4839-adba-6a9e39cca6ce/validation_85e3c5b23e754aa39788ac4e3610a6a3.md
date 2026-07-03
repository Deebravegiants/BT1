### Title
Withdrawers Do Not Earn Yield During the Withdrawal Delay Period - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

When a user calls `initiateWithdrawal`, the expected asset payout is calculated and locked at the current rsETH price. During the withdrawal delay period (default 8 days), rsETH price increases as yield accrues across the protocol. However, `_calculatePayoutAmount` enforces a hard cap at the originally locked `expectedAssetAmount`, so withdrawers receive no benefit from yield that accrues while their rsETH sits in the queue. The accrued yield is instead redistributed to remaining rsETH holders.

---

### Finding Description

In `LRTWithdrawalManager.initiateWithdrawal`, the user's rsETH is transferred to the contract and `expectedAssetAmount` is computed and stored at the current oracle prices:

```solidity
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
// = rsETHUnstaked * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

The `WithdrawalRequest` struct stores this locked `expectedAssetAmount`:

```solidity
withdrawalRequests[requestId] = WithdrawalRequest({
    rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
});
``` [2](#0-1) 

When `unlockQueue` is later called by the operator, `_calculatePayoutAmount` computes the payout as the **minimum** of the original locked amount and the current value:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
``` [3](#0-2) 

This `min()` logic means: if rsETH price has risen (yield accrued) between `initiateWithdrawal` and `unlockQueue`, `currentReturn > expectedAssetAmount`, and the user is capped at the original lower amount. The yield that accrued on the withdrawer's rsETH during the waiting period is never paid to them.

The final payout is then set and transferred:

```solidity
request.expectedAssetAmount = payoutAmount;
``` [4](#0-3) 

```solidity
_transferAsset(asset, user, request.expectedAssetAmount);
``` [5](#0-4) 

---

### Impact Explanation

Every user who initiates a withdrawal loses the yield that accrues on their rsETH during the withdrawal delay period (default 8 days, up to 16 days). The rsETH price increases as staking rewards flow into the protocol, but withdrawers are capped at the price at initiation time. This yield is not destroyed — it remains in the protocol and benefits remaining rsETH holders, constituting a transfer of yield away from withdrawers.

**Impact: High — Theft of unclaimed yield.** Every withdrawal is affected; no special conditions are required.

---

### Likelihood Explanation

This affects every single withdrawal through the standard queue path (`initiateWithdrawal` → `unlockQueue` → `completeWithdrawal`). As long as any staking yield accrues during the withdrawal delay (which is the normal operating condition), withdrawers lose yield. The withdrawal delay is initialized to 8 days. [6](#0-5) 

---

### Recommendation

Replace the `min()` logic in `_calculatePayoutAmount` with the current oracle-based value at unlock time, removing the cap at `expectedAssetAmount`. The `expectedAssetAmount` stored at initiation time should only be used for the `assetsCommitted` accounting (over-withdrawal prevention), not as a ceiling on the final payout. Alternatively, update `assetsCommitted` to track rsETH amounts rather than asset amounts, and compute the final asset payout entirely at unlock time.

---

### Proof of Concept

1. rsETH price = 1.05 ETH. User calls `initiateWithdrawal(stETH, 100e18)`.
   - `expectedAssetAmount = 100e18 * 1.05e18 / 1e18 = 105e18` stETH (assuming stETH price ≈ 1 ETH).
   - rsETH is transferred to `LRTWithdrawalManager`; `assetsCommitted[stETH] += 105e18`.

2. 8 days pass. Staking rewards accrue. rsETH price updates to 1.06 ETH.

3. Operator calls `unlockQueue(stETH, ...)`.
   - `currentReturn = 100e18 * 1.06e18 / 1e18 = 106e18` stETH.
   - `_calculatePayoutAmount` returns `min(105e18, 106e18) = 105e18`.
   - User's `expectedAssetAmount` is set to `105e18`.

4. User calls `completeWithdrawal(stETH)` and receives `105e18` stETH.

The user lost `1e18` stETH (≈ 1 ETH) of yield that accrued on their rsETH during the 8-day waiting period. This yield remains in the protocol, benefiting remaining rsETH holders. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L580-593)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L734-734)
```text
        _transferAsset(asset, user, request.expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L751-753)
```text
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });
```

**File:** contracts/LRTWithdrawalManager.sol (L804-804)
```text
            request.expectedAssetAmount = payoutAmount;
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
