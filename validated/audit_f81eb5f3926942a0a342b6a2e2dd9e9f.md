### Title
Stale Cached `rsETHPrice` in `LRTOracle` Causes Withdrawers to Receive Less Than Their Fair Share of Accrued Yield - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTOracle` stores `rsETHPrice` as a cached state variable that is only updated when `updateRSETHPrice()` is explicitly called. `LRTWithdrawalManager.initiateWithdrawal()` reads this stale cached price to compute `expectedAssetAmount`, which is then stored as a hard cap on the user's payout. Even after the price is refreshed at unlock time, `_calculatePayoutAmount` enforces `min(expectedAssetAmount, currentReturn)`, permanently locking users into the lower stale amount and causing them to forfeit accrued staking yield.

---

### Finding Description

`LRTOracle` declares `rsETHPrice` as a persistent storage variable: [1](#0-0) 

It is only updated when `updateRSETHPrice()` (a public, permissionless function) is explicitly called: [2](#0-1) 

When a user calls `initiateWithdrawal`, the function computes `expectedAssetAmount` by reading the cached `lrtOracle.rsETHPrice()`: [3](#0-2) 

`getExpectedAssetAmount` performs: [4](#0-3) 

This `expectedAssetAmount` is stored in the `WithdrawalRequest` struct: [5](#0-4) 

Later, when the operator calls `unlockWithdrawals`, `_calculatePayoutAmount` enforces: [6](#0-5) 

`currentReturn` is recalculated with the fresh price at unlock time. If the price has risen (due to staking rewards accruing since the last `updateRSETHPrice()` call), `currentReturn > expectedAssetAmount`, and the user is permanently capped at the stale lower `expectedAssetAmount`. The user can never recover the difference.

The `_updateRsETHPrice` internal function computes the live price from `_getTotalEthInProtocol()` — which includes EigenLayer restaking rewards — but this computation only runs when explicitly triggered: [7](#0-6) 

There is no automatic invocation of `updateRSETHPrice()` inside `initiateWithdrawal`. The gap between the last price update and the withdrawal initiation is the attack window.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Every user who calls `initiateWithdrawal` while `rsETHPrice` is stale (i.e., lower than the live rate due to accrued EigenLayer staking rewards) receives a permanently reduced `expectedAssetAmount`. The `min()` cap in `_calculatePayoutAmount` means the shortfall is irrecoverable even after the price is updated. The forfeited yield accrues to the protocol (diluted across remaining rsETH holders) rather than to the withdrawing user.

---

### Likelihood Explanation

**High.** `updateRSETHPrice()` is called by off-chain bots/keepers on a periodic schedule (not per-block). EigenLayer staking rewards accrue continuously. There is always a non-zero window between price updates during which `rsETHPrice` is stale. Any withdrawal initiated in this window — which is the normal operating condition — is affected. No special attacker action is required; ordinary users are harmed by routine usage.

---

### Recommendation

Call `updateRSETHPrice()` (or its internal equivalent `_updateRsETHPrice()`) at the beginning of `initiateWithdrawal` before computing `expectedAssetAmount`, analogous to the mitigation suggested in the referenced report:

```solidity
function initiateWithdrawal(address asset, uint256 rsETHUnstaked, string calldata referralId)
    external override nonReentrant whenNotPaused onlySupportedAsset(asset) onlySupportedStrategy(asset)
{
    // Refresh price before computing expectedAssetAmount
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

    if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
        revert InvalidAmountToWithdraw();
    }
    // ... rest of function
}
```

This ensures `expectedAssetAmount` always reflects the live rsETH/ETH rate inclusive of all accrued staking rewards.

---

### Proof of Concept

1. EigenLayer staking rewards accrue, increasing the true rsETH/ETH rate from `1.01e18` to `1.02e18`.
2. `updateRSETHPrice()` has not yet been called; `rsETHPrice` remains `1.01e18`.
3. Alice calls `initiateWithdrawal(stETH, 100e18, "")`.
4. `getExpectedAssetAmount` computes: `100e18 * 1.01e18 / stETHPrice` → `expectedAssetAmount` is set using the stale price.
5. The request is stored with this lower cap.
6. A keeper calls `updateRSETHPrice()` → `rsETHPrice` becomes `1.02e18`.
7. Operator calls `unlockWithdrawals`. `_calculatePayoutAmount` computes `currentReturn` using `1.02e18`, which is larger than `expectedAssetAmount`.
8. The function returns `expectedAssetAmount` (the stale lower value).
9. Alice receives less than her fair share; the yield difference is permanently lost to her. [8](#0-7) [9](#0-8) [2](#0-1)

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

**File:** contracts/LRTOracle.sol (L214-231)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L751-753)
```text
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });
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
