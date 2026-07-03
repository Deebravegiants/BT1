### Title
Stale `rsETHPrice` Exploitable During High-Gas / Market-Crash Conditions — (`contracts/LRTWithdrawalManager.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.rsETHPrice` is a manually-updated cached value. `LRTWithdrawalManager.initiateWithdrawal()` reads this cached price directly to compute how many underlying assets a user is owed. During extreme network conditions (gas spikes coinciding with a market crash or slashing event), the keeper bots that call `updateRSETHPrice()` may stop operating, leaving a stale, inflated price in storage. Any user can then call `initiateWithdrawal()` at the stale price and lock in a claim for more assets than they are entitled to, draining the protocol.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a public state variable `rsETHPrice`. [1](#0-0) 

This value is only updated when `updateRSETHPrice()` (or its manager variant) is explicitly called by an external actor. [2](#0-1) 

`LRTWithdrawalManager.getExpectedAssetAmount()` reads this cached value directly: [3](#0-2) 

`initiateWithdrawal()` calls `getExpectedAssetAmount()` to determine the user's asset claim and immediately commits that amount: [4](#0-3) 

There is no freshness check on `rsETHPrice` anywhere in this path. The oracle's downside-protection mechanism (auto-pause on large price drops) only fires inside `_updateRsETHPrice()`: [5](#0-4) 

If `updateRSETHPrice()` is never called, the protection never triggers and the stale price persists indefinitely.

---

### Impact Explanation

**Scenario — slashing event coincides with gas spike:**

1. An EigenLayer slashing event reduces the actual backing of rsETH (e.g., rsETH true value drops from 1.05 ETH to 0.90 ETH).
2. Simultaneously, Ethereum gas prices spike (as they did on 12 March 2020), making it uneconomical for keeper bots to call `updateRSETHPrice()`.
3. `rsETHPrice` remains at the pre-crash value (1.05 ETH).
4. Any user calls `initiateWithdrawal(asset, rsETHUnstaked)`. Their claim is computed as `rsETHUnstaked * 1.05e18 / assetPrice` instead of the correct `rsETHUnstaked * 0.90e18 / assetPrice` — a ~16.7% over-allocation per withdrawal.
5. `assetsCommitted[asset]` is incremented by the inflated amount, locking those assets for the attacker.
6. When the withdrawal is eventually completed via `completeWithdrawal()`, the user receives the inflated `expectedAssetAmount` stored at request time. [6](#0-5) 

The over-allocated assets come directly from other users' deposits, constituting a direct theft of funds. If many users race to withdraw at the stale price, the protocol can be rendered insolvent — exactly the MakerDAO March 2020 scenario described in the reference report.

**Impact classification:** Critical — direct theft of user funds at rest.

---

### Likelihood Explanation

- Gas spikes and market crashes are historically correlated (March 2020, May 2021, November 2022).
- `updateRSETHPrice()` is a permissionless public function, but it costs non-trivial gas (it iterates over all supported assets and all NodeDelegators). During a gas spike, keeper bots routinely hit cost limits or are deactivated.
- No on-chain staleness guard exists; the protocol has no maximum age for `rsETHPrice`.
- The attacker does not need to be sophisticated — any user who notices the price has not been updated can exploit this passively by simply calling `initiateWithdrawal()`.

**Likelihood classification:** Medium — requires a correlated gas-spike + price-drop event, which is historically inevitable.

---

### Recommendation

1. **Add a staleness deadline to `rsETHPrice`.** Store a `rsETHPriceLastUpdated` timestamp alongside `rsETHPrice`. In `initiateWithdrawal()` and `getExpectedAssetAmount()`, revert if `block.timestamp - rsETHPriceLastUpdated > MAX_PRICE_AGE` (e.g., 4 hours).

2. **Compute price on-demand in the withdrawal path.** Instead of reading the cached `rsETHPrice`, call a view function that recomputes the rate from current TVL (similar to `_getTotalEthInProtocol()`) so the withdrawal path always uses a fresh value.

3. **Auto-pause withdrawals when the price is stale.** If `rsETHPrice` has not been updated within `MAX_PRICE_AGE`, `initiateWithdrawal()` should revert, preventing exploitation during keeper outages.

---

### Proof of Concept

```
State before attack:
  rsETHPrice = 1.05e18  (last updated 6 hours ago, before slashing)
  actual rsETH backing = 0.90 ETH per rsETH (post-slash, not yet reflected)
  gas price = 500 gwei (keepers offline)

Attacker holds: 100e18 rsETH

Step 1: Attacker calls initiateWithdrawal(ETH, 100e18)
  expectedAssetAmount = 100e18 * 1.05e18 / 1e18 = 105 ETH   ← stale price used
  assetsCommitted[ETH] += 105 ETH

Step 2: After withdrawalDelayBlocks pass, operator calls unlockQueue()
  _calculatePayoutAmount uses min(105 ETH, currentReturn)
  currentReturn = 100e18 * 0.90e18 / 1e18 = 90 ETH  (if price updated by then)
  → payout = min(105, 90) = 90 ETH  ← capped at current return

  BUT if rsETHPrice is still stale when unlockQueue() is called:
  currentReturn = 100e18 * 1.05e18 / 1e18 = 105 ETH
  → payout = 105 ETH  ← full over-allocation paid out

Step 3: Attacker calls completeWithdrawal() and receives 105 ETH
  Correct entitlement: 90 ETH
  Stolen: 15 ETH (16.7% of position)
```

The `_calculatePayoutAmount` min-cap only protects if `rsETHPrice` has been updated before `unlockQueue()` is called. If the gas spike persists through the withdrawal delay window (8 days by default), the full stale-price over-allocation is paid out. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L28-29)
```text
    uint256 public override rsETHPrice;
    uint256 public pricePercentageLimit;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L270-281)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-737)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
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
