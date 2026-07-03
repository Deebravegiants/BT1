### Title
Unpermissioned `updateRSETHPrice()` Allows Any Caller to Trigger Protocol-Wide Auto-Pause — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` carries no caller restriction beyond `whenNotPaused`. Any externally-owned account or contract can invoke it at will. Inside `_updateRsETHPrice()`, a price-drop guard compares the freshly computed rsETH price against `highestRsethPrice`; if the drop exceeds `pricePercentageLimit`, the function immediately pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` itself. Because the entry point is unrestricted, an unprivileged attacker can race to call it the moment on-chain conditions satisfy the threshold, forcing a protocol-wide pause without any privileged key.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no role modifier: [1](#0-0) 

It delegates immediately to `_updateRsETHPrice()`, which contains the downside-protection branch: [2](#0-1) 

When `isPriceDecreaseOffLimit` is true the function calls `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` on the oracle itself, then returns early without updating `rsETHPrice`. All three pauses are triggered by the single public call — no privileged role is required.

The symmetric upside guard does enforce a role check: [3](#0-2) 

So the protocol intentionally restricts who can push a price *increase* past the threshold, but imposes no equivalent restriction on who can push a price *decrease* past the threshold and trigger the pause.

---

### Impact Explanation

**Temporary freezing of funds (Medium).**

Once the three-contract pause is triggered:
- `LRTDepositPool` rejects all new deposits.
- `LRTWithdrawalManager` rejects all withdrawal claims.
- `LRTOracle` itself is paused, blocking further price updates via the public path.

Unpausing requires an `onlyLRTAdmin` call to each contract. Until that governance action executes, every user's in-flight withdrawal and every pending deposit is frozen. [4](#0-3) 

---

### Likelihood Explanation

**Realistic.** The attacker needs only two conditions to hold simultaneously:

1. `pricePercentageLimit > 0` — set by the admin and expected to be non-zero in production (the variable exists precisely to enforce a daily price-movement cap).
2. The live rsETH price computed from current EigenLayer TVL is below `highestRsethPrice` by more than `pricePercentageLimit * highestRsethPrice`.

Condition 2 can arise from ordinary events: an LST oracle price dip, a slashing event on an EigenLayer operator, or a temporary imbalance in the underlying asset mix. The attacker does not need to manufacture the price drop — they only need to observe it and call `updateRSETHPrice()` before any legitimate keeper does. Because the function is public and costs only gas, the attacker can front-run any keeper bot.

---

### Recommendation

Add a caller restriction to `updateRSETHPrice()` that mirrors the upside guard. Two options:

1. **Restrict to a keeper/manager role** — only allow addresses with `LRTConstants.MANAGER` (or a dedicated `KEEPER_ROLE`) to call `updateRSETHPrice()`. Expose a separate, fully view-only function for off-chain price reads.
2. **Separate the pause trigger from the public price read** — keep a permissionless read path but move the auto-pause logic into a role-gated function (`updateRSETHPriceAsManager` already exists for the upside case; extend it to cover the downside pause as well).

At minimum, add a comment documenting that the function is intentionally public and explaining why the auto-pause trigger is safe to expose to arbitrary callers.

---

### Proof of Concept

```
Preconditions:
  - pricePercentageLimit = 1e16  (1%, set by admin)
  - highestRsethPrice = 1.05e18  (rsETH all-time high)
  - Current EigenLayer TVL implies newRsETHPrice = 1.03e18
    → diff = 0.02e18 > 1e16 * 1.05e18 / 1e18 = 1.05e16  ✓ threshold exceeded

Attack:
  1. Attacker calls LRTOracle.updateRSETHPrice() from any EOA.
  2. _updateRsETHPrice() computes newRsETHPrice = 1.03e18.
  3. isPriceDecreaseOffLimit = true.
  4. lrtDepositPool.pause() executes  → deposits frozen.
  5. withdrawalManager.pause() executes → withdrawal claims frozen.
  6. LRTOracle._pause() executes → oracle paused.
  7. Function returns early; rsETHPrice is NOT updated.

Result:
  - All user deposits and withdrawal claims are blocked until
    an LRTAdmin manually unpauses each of the three contracts.
  - The attacker spent only gas; no capital at risk.
``` [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L142-146)
```text
    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L260-266)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
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
