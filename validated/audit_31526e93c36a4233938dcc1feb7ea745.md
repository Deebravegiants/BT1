### Title
`highestRsethPrice` Is a One-Way Ratchet With No Reset Function, Enabling Permanent Auto-Pause Griefing After Price Drop - (File: `contracts/LRTOracle.sol`)

### Summary

`LRTOracle` stores `highestRsethPrice` as an all-time-high watermark that can only ever increase. There is no admin function to lower or reset it. After any significant price drop (e.g., from an EigenLayer slashing event), the downside-protection logic auto-pauses the entire protocol. Because `highestRsethPrice` is permanently anchored to the old peak, every subsequent call to the public `updateRSETHPrice()` re-triggers the auto-pause, creating a griefing loop that keeps deposits and withdrawals frozen until the admin disables the protection entirely.

### Finding Description

In `LRTOracle._updateRsETHPrice()`, `highestRsethPrice` is updated only when the new price exceeds it:

```solidity
// update highest price if new price exceeds it
if (newRsETHPrice > highestRsethPrice) {
    highestRsethPrice = newRsETHPrice;
}
``` [1](#0-0) 

There is no corresponding path to decrease `highestRsethPrice`. The downside-protection block compares the current price against this permanent peak:

```solidity
if (newRsETHPrice < highestRsethPrice) {
    ...
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;
    }
``` [2](#0-1) 

Once `highestRsethPrice` is set to a high watermark, any future price that is more than `pricePercentageLimit` below that watermark will unconditionally auto-pause `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` itself. Because `highestRsethPrice` never decreases, the condition remains true on every subsequent call. The public entry point `updateRSETHPrice()` is callable by anyone when the contract is not paused:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [3](#0-2) 

The attack loop is:
1. Price drops significantly from `highestRsethPrice` (e.g., slashing).
2. Anyone calls `updateRSETHPrice()` → protocol auto-pauses.
3. Admin calls `unpause()` on all three contracts.
4. Anyone immediately calls `updateRSETHPrice()` again → protocol auto-pauses again.
5. Repeat indefinitely.

The admin's only escape is to call `setPricePercentageLimit(0)`, which disables the downside protection entirely — a significant security trade-off. [4](#0-3) 

### Impact Explanation

Every call to `updateRSETHPrice()` after a significant price drop re-pauses `LRTDepositPool` and `LRTWithdrawalManager`. Users cannot deposit ETH/LSTs and cannot complete pending withdrawals. This constitutes **temporary (potentially indefinite) freezing of funds** — matching the "Medium: Temporary freezing of funds" impact tier. The freeze persists until the admin either disables the price-drop guard or the price recovers above the threshold.

### Likelihood Explanation

EigenLayer slashing events are a documented, realistic risk for any restaking protocol. A meaningful slash could drop the rsETH price by several percent from its all-time high. Once that happens, the griefing loop requires no special privilege — any EOA can call the public `updateRSETHPrice()` to re-trigger the pause after each admin unpause. Likelihood is **Medium**.

### Recommendation

Add an admin-restricted function to reset `highestRsethPrice` to the current `rsETHPrice`, allowing the protocol to re-anchor its downside-protection baseline after a verified slashing event:

```solidity
function resetHighestRsethPrice() external onlyLRTAdmin {
    highestRsethPrice = rsETHPrice;
    emit HighestRsethPriceReset(rsETHPrice);
}
```

This mirrors the fix in the referenced report: directly assign the state variable from the parameter rather than gating the assignment behind a one-directional condition.

### Proof of Concept

1. `highestRsethPrice` is set to `1.10 ETH` after a period of rewards accrual.
2. An EigenLayer slashing event reduces total ETH in protocol; `_getTotalEthInProtocol()` now yields a price of `1.04 ETH`.
3. `pricePercentageLimit` is set to `5e16` (5%).
4. `diff = 1.10e18 - 1.04e18 = 0.06e18`; `pricePercentageLimit.mulWad(highestRsethPrice) = 0.055e18`; `0.06e18 > 0.055e18` → `isPriceDecreaseOffLimit = true`.
5. Protocol auto-pauses. [5](#0-4) 
6. Admin calls `unpause()` on `LRTOracle`, `LRTDepositPool`, `LRTWithdrawalManager`.
7. Attacker (any EOA) calls `updateRSETHPrice()`. Price is still `1.04 ETH`; `highestRsethPrice` is still `1.10 ETH` (it never decreased). Same condition fires → protocol auto-pauses again. [1](#0-0) 
8. Steps 6–7 repeat indefinitely, keeping user funds frozen.

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

**File:** contracts/LRTOracle.sol (L270-282)
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
            }
```

**File:** contracts/LRTOracle.sol (L293-296)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```
