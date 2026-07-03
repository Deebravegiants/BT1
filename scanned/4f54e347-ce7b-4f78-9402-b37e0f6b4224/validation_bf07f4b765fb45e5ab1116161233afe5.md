### Title
Publicly Callable `updateRSETHPrice()` Triggers Protocol-Wide Pause on Any Price Downtick, Causing Temporary Freezing of All User Funds — (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is an unrestricted public function. When the computed rsETH price falls below `highestRsethPrice × (1 − pricePercentageLimit)`, it atomically pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` itself. Any unprivileged caller can invoke this function immediately after any natural price-decreasing event (EigenLayer slashing, LST oracle downtick) to freeze the entire protocol, blocking all deposits and withdrawals until an admin manually unpauses.

---

### Finding Description

`updateRSETHPrice()` carries no access control — only a `whenNotPaused` guard:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Inside `_updateRsETHPrice()`, the downside-protection branch is:

```solidity
// contracts/LRTOracle.sol L270-282
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;   // rsETHPrice is NOT updated; stale high price is preserved
    }
    ...
}
```

Three consequences fire atomically:
1. `LRTDepositPool` is paused → `depositETH` / `depositAsset` revert.
2. `LRTWithdrawalManager` is paused → `initiateWithdrawal`, `completeWithdrawal`, `instantWithdrawal`, and `unlockQueue` all revert.
3. `LRTOracle` itself is paused → `updateRSETHPrice()` can no longer be called, so the oracle is frozen at the stale (pre-drop) price.

The price used for withdrawal accounting (`lrtOracle.rsETHPrice()`) is read directly from the stale stored value:

```solidity
// contracts/LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

Because `rsETHPrice` is not updated when the pause fires (the function returns early), the stale high price persists in storage. Any withdrawal that was already queued before the pause will be processed at this stale price once the admin unpauses — potentially over-paying users relative to the true post-slashing value, or under-paying if the admin updates the price first.

The attack surface is structurally analogous to the reported whale-sniping pattern: a publicly reachable action (calling `updateRSETHPrice()`) changes a global protocol state (triggers the pause threshold) and produces an adverse condition (fund freeze) that the caller can time to maximise harm.

---

### Impact Explanation

- **All deposits frozen** — `LRTDepositPool.depositETH` / `depositAsset` revert while paused.
- **All withdrawals frozen** — `initiateWithdrawal`, `completeWithdrawal`, `instantWithdrawal`, and `unlockQueue` in `LRTWithdrawalManager` revert while paused.
- **Oracle frozen at stale price** — `rsETHPrice` is not updated on the pause path; the stale value is used for all subsequent withdrawal accounting once unpaused.
- **Recovery requires privileged admin action** — only `onlyLRTAdmin` can call `unpause()` on each contract; there is no automatic recovery or time-bounded grace period.

Impact classification: **Medium — Temporary freezing of funds** (all user deposits and pending withdrawals are inaccessible for the duration of the pause).

---

### Likelihood Explanation

- EigenLayer slashing events and LST oracle price corrections are realistic, recurring occurrences.
- The attacker needs zero capital pre-positioning; the only cost is gas for a single public call.
- `pricePercentageLimit` is a configurable parameter; at any non-zero setting the threshold can be breached by a sufficiently large price move.
- The call can be made by any EOA or contract immediately after observing a qualifying price drop on-chain.

Likelihood: **Medium**.

---

### Recommendation

1. **Restrict `updateRSETHPrice()` to authorised callers** (e.g., `onlyLRTManager` or a keeper role), preventing arbitrary actors from triggering the pause path.
2. **Introduce a grace period** before the pause fires (analogous to the 15-minute grace period recommended in the original report), giving the protocol time to distinguish transient oracle noise from genuine slashing.
3. **Update `rsETHPrice` before returning** on the pause path, so the stored price reflects reality when the protocol is unpaused, preventing stale-price accounting errors in `getExpectedAssetAmount`.
4. **Bound the grace period** between a minimum (e.g., 1 hour) and a maximum (e.g., 2 days) to balance attacker risk against user reaction time, as Cantina recommended for the analogous CDP grace period.

---

### Proof of Concept

```
Precondition: pricePercentageLimit > 0 (e.g., 5 × 10^16 = 5%)
              highestRsethPrice = 1.10 ETH (set during a prior price peak)

Step 1. An EigenLayer slashing event reduces totalETHInProtocol.
        The LST oracle reflects the loss; newRsETHPrice drops to ~1.03 ETH.
        diff = 1.10 - 1.03 = 0.07 ETH  >  0.05 × 1.10 = 0.055 ETH  → threshold breached.

Step 2. Attacker (any EOA) calls:
            LRTOracle.updateRSETHPrice()

Step 3. _updateRsETHPrice() executes the downside-protection branch:
            lrtDepositPool.pause()        // deposits frozen
            withdrawalManager.pause()     // withdrawals frozen
            _pause()                      // oracle frozen; rsETHPrice NOT updated
            return

Step 4. All user calls to depositETH, depositAsset, initiateWithdrawal,
        completeWithdrawal, instantWithdrawal, and unlockQueue revert with
        "Pausable: paused" until an admin calls unpause() on each contract.

Step 5. rsETHPrice remains at 1.10 ETH (stale). When admin unpauses without
        first calling updateRSETHPriceAsManager(), withdrawal accounting
        over-values rsETH, paying out more underlying than the post-slash
        rate warrants — a secondary accounting discrepancy.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L236-241)
```text
        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L269-282)
```text
        // downside protection — pause if price drops too far
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
            }
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

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
