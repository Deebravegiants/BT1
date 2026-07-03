### Title
`currentPeriodMintedAmount` is never decremented on `burnFrom`, causing premature daily mint limit exhaustion - (File: contracts/RSETH.sol)

### Summary
The `RSETH` contract increments `currentPeriodMintedAmount` on every mint but never decrements it when rsETH is burned. No admin function exists to reset `currentPeriodMintedAmount` within the same 24-hour period. When users initiate withdrawals (burning rsETH), the daily mint capacity is not restored, causing the limit to be exhausted faster than intended and temporarily blocking legitimate depositors.

### Finding Description
The `checkDailyMintLimit` modifier in `RSETH.sol` tracks cumulative minting within a 24-hour window via `currentPeriodMintedAmount`: [1](#0-0) 

Every call to `mint` (triggered by `LRTDepositPool` on user deposits) increments `currentPeriodMintedAmount`. However, `burnFrom` — called by the withdrawal manager when users initiate withdrawals — performs no corresponding decrement: [2](#0-1) 

The only admin setter for the limit is `setMaxMintAmountPerDay`, which changes the cap but does not touch `currentPeriodMintedAmount`: [3](#0-2) 

There is no function anywhere in `RSETH.sol` that decrements or resets `currentPeriodMintedAmount` within the active period. The only reset path is the automatic rollover when `block.timestamp >= periodStartTime + 1 days`: [4](#0-3) 

This is the direct analog to the external report: just as `MintController` had no `decrementMinterAllowance` (requiring a full minter reconfiguration to reduce allowance), `RSETH` has no mechanism to decrement `currentPeriodMintedAmount` when tokens are burned, requiring a full 24-hour wait to restore capacity.

### Impact Explanation
**Medium — Temporary freezing of deposits.** When the daily mint limit is reached and rsETH is subsequently burned (via normal user withdrawals), new depositors are blocked from minting for up to 24 hours even though the net outstanding rsETH supply is below the daily cap. The `checkDailyMintLimit` modifier will revert with `DailyMintLimitExceeded` for all new deposit attempts until the period rolls over. [5](#0-4) 

### Likelihood Explanation
**Medium.** This occurs naturally whenever users request withdrawals within the same 24-hour window as deposits — a routine operational pattern. No adversarial action is required; the condition arises from normal protocol usage. The higher the daily throughput relative to the cap, the more frequently this blocks new depositors.

### Recommendation
Decrement `currentPeriodMintedAmount` inside `burnFrom` when the burn occurs within the active period. If `currentPeriodMintedAmount >= amount`, subtract `amount`; otherwise clamp to zero. This mirrors the complementary decrement pattern recommended in the external report's update.

```solidity
function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
    _enforceNotBlocked(account);
    // Restore daily mint capacity when burning within the active period
    if (block.timestamp < periodStartTime + 1 days) {
        currentPeriodMintedAmount = currentPeriodMintedAmount >= amount
            ? currentPeriodMintedAmount - amount
            : 0;
    }
    _burn(account, amount);
}
```

### Proof of Concept
1. Admin calls `setMaxMintAmountPerDay(1000 ether)`.
2. Users deposit ETH via `LRTDepositPool.depositETH` → `RSETH.mint` is called repeatedly → `currentPeriodMintedAmount` reaches `1000 ether`.
3. Some users initiate withdrawals → `LRTWithdrawalManager` calls `RSETH.burnFrom` → 500 ether of rsETH is destroyed → `currentPeriodMintedAmount` remains at `1000 ether`.
4. A new depositor calls `LRTDepositPool.depositETH` → `RSETH.mint` → `checkDailyMintLimit` evaluates `1000 ether + depositAmount > 1000 ether` → reverts `DailyMintLimitExceeded(1000 ether + depositAmount, 1000 ether)`. [6](#0-5) 

5. All new depositors are blocked for up to 24 hours until `periodStartTime + 1 days` elapses and the automatic reset fires, despite 500 ether of net rsETH having been removed from circulation.

### Citations

**File:** contracts/RSETH.sol (L42-56)
```text
    modifier checkDailyMintLimit(uint256 amount) {
        // Check if we need to reset the period if it has been more than 24 hours
        if (block.timestamp >= periodStartTime + 1 days) {
            currentPeriodMintedAmount = 0;
            periodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedAmount + amount > maxMintAmountPerDay) {
            revert DailyMintLimitExceeded(currentPeriodMintedAmount + amount, maxMintAmountPerDay);
        }

        currentPeriodMintedAmount += amount;
        _;
    }
```

**File:** contracts/RSETH.sol (L125-128)
```text
    function setMaxMintAmountPerDay(uint256 _maxMintAmountPerDay) external onlyLRTManager {
        maxMintAmountPerDay = _maxMintAmountPerDay;
        emit MaxMintAmountPerDayUpdated(_maxMintAmountPerDay);
    }
```

**File:** contracts/RSETH.sol (L229-240)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }
```

**File:** contracts/RSETH.sol (L245-248)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
```
