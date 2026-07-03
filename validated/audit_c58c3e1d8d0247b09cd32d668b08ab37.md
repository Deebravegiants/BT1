### Title
Zero-Value Sentinel Bypasses Price-Protection Checks in `updateRSETHPrice` — (File: `contracts/LRTOracle.sol`)

### Summary
`LRTOracle._updateRsETHPrice()` uses `pricePercentageLimit > 0` as a sentinel guard before applying both the upside price-increase revert (for non-managers) and the downside auto-pause. When `pricePercentageLimit` is zero — its default uninitialized value, or any value an admin explicitly sets to mean "0% tolerance" — both guards are silently skipped, disabling all price-movement protection for the publicly callable `updateRSETHPrice()`.

### Finding Description
`_updateRsETHPrice()` contains two safety checks gated on the same sentinel:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
// ...
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [1](#0-0) 

When `pricePercentageLimit == 0`, both boolean expressions short-circuit to `false` regardless of the actual price movement magnitude. Consequently:

1. **Upside bypass** — the branch that reverts for non-manager callers when the price spikes is never reached.
2. **Downside bypass** — the branch that auto-pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` on a significant price drop is never reached.

`pricePercentageLimit` starts at zero (Solidity default) and is only set by `setPricePercentageLimit`, which accepts zero without restriction:

```solidity
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
``` [2](#0-1) 

An admin who intends "0% tolerance" (any price change should trigger the guard) would naturally set the value to `0`, but this instead disables both guards entirely — the same zero-as-sentinel ambiguity as the reported UniV3 fee bypass.

### Impact Explanation
- **Downside**: After a slashing event or accounting error that causes the computed rsETH price to fall sharply, any unprivileged caller can invoke `updateRSETHPrice()` and commit the depressed price without triggering the auto-pause that is supposed to halt deposits and withdrawals for investigation. The protocol continues operating at the lower price, failing to deliver the promised safety guarantee.
- **Upside**: A non-manager can commit an anomalously high price update (e.g., caused by a temporary ETH donation inflating `_getTotalEthInProtocol`) without the revert that would otherwise require manager intervention.

Impact classification: **Low — contract fails to deliver promised safety returns (auto-pause mechanism) without direct loss of principal.**

### Likelihood Explanation
`pricePercentageLimit` is zero from deployment until an admin explicitly sets it. Any window between deployment and configuration, or any future admin call that resets it to zero, leaves the protocol unprotected. `updateRSETHPrice()` is a public, permissionless function callable by anyone. [3](#0-2) 

### Recommendation
Replace the `> 0` sentinel with an explicit "disabled" flag, or use a dedicated non-zero sentinel value (e.g., `type(uint256).max`) to mean "no limit." Alternatively, treat `pricePercentageLimit == 0` as "0% tolerance" (always enforce the check) and introduce a separate boolean `isPriceProtectionEnabled` to opt out:

```solidity
// Option A: separate disable flag
bool public priceProtectionEnabled;

bool isPriceIncreaseOffLimit =
    priceProtectionEnabled && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

Also add a lower-bound guard in `setPricePercentageLimit` to reject zero if the intent is always to enforce a non-zero tolerance.

### Proof of Concept
1. Deploy `LRTOracle` (or leave `pricePercentageLimit` at its default of `0`).
2. Simulate a slashing event: reduce the ETH balance tracked by `NodeDelegator` so that `_getTotalEthInProtocol()` returns a value significantly below `rsethSupply * rsETHPrice`.
3. Call `updateRSETHPrice()` from any EOA (no role required).
4. Observe: `isPriceDecreaseOffLimit` evaluates to `false` (because `pricePercentageLimit > 0` is `false`), the auto-pause branch is never entered, and `rsETHPrice` is updated to the depressed value while `LRTDepositPool` and `LRTWithdrawalManager` remain unpaused.
5. Users continue to deposit and withdraw against the post-slash price with no circuit-breaker intervention. [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L125-128)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
    }
```

**File:** contracts/LRTOracle.sol (L256-282)
```text
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
        }

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
