### Title
Unrestricted `updateRSETHPrice()` Allows Any Caller to Trigger Protocol-Wide Pause — (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` carries no access-control modifier. Any externally-owned account can invoke it at will. Inside the function, when the computed rsETH price has fallen more than `pricePercentageLimit` below `highestRsethPrice`, the oracle immediately pauses both `LRTDepositPool` and `LRTWithdrawalManager` on behalf of the oracle contract (which holds `PAUSER_ROLE`). An unprivileged depositor or any public caller can therefore freeze all protocol deposits and withdrawals without holding any privileged role.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no role guard: [1](#0-0) 

The companion function `updateRSETHPriceAsManager()` is explicitly gated with `onlyLRTManager`, confirming the protocol recognises that privileged access is sometimes required for price updates, yet the public entry point is left open: [2](#0-1) 

Inside `_updateRsETHPrice()`, the downside-protection branch unconditionally pauses the deposit pool and withdrawal manager when the price drop exceeds the configured threshold: [3](#0-2) 

`LRTDepositPool.pause()` is normally restricted to `PAUSER_ROLE`: [4](#0-3) 

Because the oracle contract itself holds `PAUSER_ROLE` and `updateRSETHPrice()` is unrestricted, any caller can route through the oracle to exercise that privileged role without possessing it directly.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

When the pause fires, `LRTDepositPool` (blocking all `depositETH` / `depositAsset` calls) and `LRTWithdrawalManager` (blocking all withdrawal claims) are both paused simultaneously. User funds are inaccessible until an admin with `DEFAULT_ADMIN_ROLE` manually unpauses each contract. The oracle itself is also self-paused, preventing further price updates until unpaused by an admin. [5](#0-4) 

---

### Likelihood Explanation

**Medium.**

The condition requires `newRsETHPrice` to have fallen more than `pricePercentageLimit` below `highestRsethPrice`. This can occur naturally after a slashing event, a sharp drop in an underlying LST oracle price (e.g. Chainlink feed for stETH/ETH), or a temporary liquidity imbalance in an integrated strategy. Once the on-chain condition is satisfied, any observer — including a competing protocol, a griefing bot, or a user who simply wants to block withdrawals — can call `updateRSETHPrice()` with zero capital and no special role to lock the protocol. The attacker bears only gas cost.

---

### Recommendation

Add `onlyLRTManager` (or a dedicated keeper role) to `updateRSETHPrice()`, consistent with the access control already applied to `updateRSETHPriceAsManager()`. If permissionless price refreshes are desired for liveness, separate the pause-triggering logic into a distinct function callable only by `PAUSER_ROLE`, and keep the public entry point limited to read-only price computation.

```solidity
// Before (vulnerable)
function updateRSETHPrice() public whenNotPaused {

// After (suggested)
function updateRSETHPrice() external whenNotPaused onlyLRTManager {
```

---

### Proof of Concept

1. Assume `pricePercentageLimit = 1e16` (1%) and `highestRsethPrice = 1.05e18`.
2. A Chainlink feed for an underlying LST drops, causing `_getTotalEthInProtocol()` to return a value that yields `newRsETHPrice = 1.03e18` — a ~1.9% drop, exceeding the 1% limit.
3. Attacker (any EOA) calls `LRTOracle.updateRSETHPrice()`.
4. `_updateRsETHPrice()` reaches the downside-protection branch: `diff = 0.02e18 > 0.01e16 * 1.05 ≈ 0.0105e18` → `isPriceDecreaseOffLimit = true`.
5. Oracle calls `lrtDepositPool.pause()` and `withdrawalManager.pause()` using its own `PAUSER_ROLE`, then self-pauses.
6. All user deposits and withdrawal claims revert with `Pausable: paused` until an admin intervenes. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L91-96)
```text
    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
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

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L348-351)
```text
    /// @dev Triggers stopped state. Contract must not be paused.
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```
