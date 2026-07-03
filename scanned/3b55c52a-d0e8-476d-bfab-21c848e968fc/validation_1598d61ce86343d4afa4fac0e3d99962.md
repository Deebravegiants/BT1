### Title
`NodeDelegator.getAssetUnstaking()` Uses Raw `scaledShares` Without Applying Current `slashingFactor`, Inflating `rsETHPrice` Post-Slash and Enabling Direct Theft of At-Rest User Funds - (`contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.getAssetUnstaking()` reads raw `scaledShares` from EigenLayer's `getQueuedWithdrawals()` and converts them to underlying tokens without applying the current `slashingFactor`. In contrast, `getAssetBalance()` correctly applies the slashing factor via `getWithdrawableShares()`. After an operator slash, `getTotalAssetDeposits()` and therefore `LRTOracle._updateRsETHPrice()` overstate `totalETHInProtocol`, inflating `rsETHPrice`. An attacker can lock in this inflated price and initiate withdrawals at a rate the vault cannot honour, draining at-rest funds from other users.

---

### Finding Description

**Root cause — `getAssetUnstaking()` ignores `slashingFactor`** [1](#0-0) 

The function calls `_getDelegationManager().getQueuedWithdrawals(address(this))` and uses the returned `withdrawalShares` directly. Per the `Withdrawal` struct comment in `IDelegationManager.sol`, the stored field is `scaledShares` — raw values that must be multiplied by the operator's current `maxMagnitude` (the `slashingFactor`) at completion time to account for any slashing that occurred during the delay period: [2](#0-1) 

`SlashingLib.scaleForCompleteWithdrawal()` makes this explicit: [3](#0-2) 

`getAssetUnstaking()` never calls this; it passes the raw `scaledShares` straight into `strategy.sharesToUnderlyingView()`, returning a pre-slash token amount even after the operator has been slashed.

**Contrast with `getAssetBalance()`**

`getAssetBalance()` delegates to `NodeDelegatorHelper.getAssetBalance()`, which calls `getWithdrawableShares()` → `DelegationManager.getWithdrawableShares()`. EigenLayer's `getWithdrawableShares` applies the current `slashingFactor` internally, so it correctly reflects post-slash reality: [4](#0-3) [5](#0-4) 

**Propagation through accounting**

`LRTDepositPool.getAssetDistributionData()` sums both values: [6](#0-5) 

`getTotalAssetDeposits()` adds them together: [7](#0-6) 

`LRTOracle._getTotalEthInProtocol()` uses this inflated total: [8](#0-7) 

`updateRSETHPrice()` is public and callable by anyone: [9](#0-8) 

**Withdrawal commitment at inflated price**

`LRTWithdrawalManager.initiateWithdrawal()` locks in `expectedAssetAmount` using the current (inflated) `rsETHPrice`: [10](#0-9) 

When `completeUnstaking()` later settles with EigenLayer, the vault receives only `scaledShares × slashingFactor` tokens — less than what was committed — leaving other users' funds short.

---

### Impact Explanation

**Direct theft of at-rest user funds (Critical).**

After a slash, the attacker:
1. Calls `LRTOracle.updateRSETHPrice()` to lock in the inflated price.
2. Calls `LRTWithdrawalManager.initiateWithdrawal()` at the inflated rate, committing more asset than the vault will actually receive.
3. Waits for `completeUnstaking()` to settle (receiving only the slashed amount).
4. Calls `completeWithdrawal()` and receives the over-committed amount, draining funds that belong to other depositors.

The invariant `sum(tokens_received_by_all_withdrawers) ≤ sum(tokens_ever_deposited)` breaks.

---

### Likelihood Explanation

- EigenLayer operator slashing is a live, permissionless protocol event — no admin compromise is required.
- `updateRSETHPrice()` is public; any EOA can call it immediately after a slash.
- The price-decrease circuit-breaker only triggers if the *computed* (inflated) price drops more than `pricePercentageLimit` below `highestRsethPrice`. Because `getAssetUnstaking()` inflates the total, the computed price is higher than actual, making the circuit-breaker less likely to fire for moderate slashes.
- The `getAvailableAssetAmount` check in `initiateWithdrawal()` uses the same inflated accounting, so it does not prevent over-commitment.

---

### Recommendation

Apply the current `slashingFactor` inside `getAssetUnstaking()`. For each queued withdrawal, retrieve the operator's current `maxMagnitude` from the `AllocationManager` and multiply `scaledShares` by it before converting to underlying tokens — mirroring what `SlashingLib.scaleForCompleteWithdrawal()` does at completion time. Alternatively, call `DelegationManager.getWithdrawableShares()` for the queued withdrawal strategies and use those already-adjusted values, consistent with how `getAssetBalance()` is implemented.

---

### Proof of Concept

```
Setup (fork or mock EigenLayer with slashing support):
  1. Deploy NDC, delegate to operator O.
  2. Deposit 100 stETH into strategy; NDC holds 100 shares.
  3. NDC.initiateUnstaking(strategy, 100 shares) → queued withdrawal with scaledShares = 100.
  4. Slash operator O by 20% → slashingFactor = 0.8e18.
     EigenLayer burns 20 shares; vault will receive only 80 stETH on completion.

Accounting check (before price update):
  - getAssetBalance(stETH)   → 0  (shares removed from strategy on queue)
  - getAssetUnstaking(stETH) → 100 stETH  (raw scaledShares, no slashingFactor applied)
  - getTotalAssetDeposits()  → 100 stETH  (inflated; actual = 80)

Attack:
  5. Attacker calls LRTOracle.updateRSETHPrice().
     totalETHInProtocol = 100 (inflated) → rsETHPrice inflated.
  6. Attacker calls LRTWithdrawalManager.initiateWithdrawal(stETH, rsETHAmount)
     expectedAssetAmount = 100 stETH committed.
  7. Operator calls NDC.completeUnstaking() → vault receives 80 stETH.
  8. Attacker calls completeWithdrawal() → receives 100 stETH (if vault has liquidity from others).
     Other users are short 20 stETH.

Assert: sum(received) = 100 > sum(actual_vault_assets) = 80. Invariant broken.
```

### Citations

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```

**File:** contracts/external/eigenlayer/interfaces/IDelegationManager.sol (L122-133)
```text
        IStrategy[] strategies;
        // Array containing the amount of staker's scaledShares for withdrawal in each Strategy in the `strategies`
        // array
        // Note that these scaledShares need to be multiplied by the operator's maxMagnitude and
        // beaconChainScalingFactor at completion to include
        // slashing occurring during the queue withdrawal delay. This is because scaledShares = sharesToWithdraw /
        // (maxMagnitude * beaconChainScalingFactor)
        // at queue time. beaconChainScalingFactor is simply equal to 1 if the strategy is not the beaconChainStrategy.
        // To account for slashing, we later multiply scaledShares * maxMagnitude * beaconChainScalingFactor at the
        // earliest possible completion time
        // to get the withdrawn shares after applying slashing during the delay period.
        uint256[] scaledShares;
```

**File:** contracts/external/eigenlayer/libraries/SlashingLib.sol (L82-84)
```text
    function scaleForCompleteWithdrawal(uint256 scaledShares, uint256 slashingFactor) internal pure returns (uint256) {
        return scaledShares.mulWad(slashingFactor);
    }
```

**File:** contracts/NodeDelegatorHelper.sol (L31-39)
```text
    function getAssetBalance(ILRTConfig lrtConfig, address asset) internal view returns (uint256) {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            return 0;
        }
        uint256 withdrawableShare = getWithdrawableShare(lrtConfig, IStrategy(strategy));

        return IStrategy(strategy).sharesToUnderlyingView(withdrawableShare);
    }
```

**File:** contracts/NodeDelegatorHelper.sol (L52-65)
```text
    function getWithdrawableShare(
        ILRTConfig lrtConfig,
        IStrategy strategy
    )
        internal
        view
        returns (uint256 withdrawableShare)
    {
        IStrategy[] memory strategies = new IStrategy[](1);
        strategies[0] = strategy;

        uint256[] memory withdrawableShares = getWithdrawableShares(lrtConfig, strategies);
        return withdrawableShares[0];
    }
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

**File:** contracts/LRTDepositPool.sol (L450-451)
```text
            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```
