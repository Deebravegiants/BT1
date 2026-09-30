# [H] Incorrect lockedPremium Update In HegicOperationalTreasury::lockLiquidityFor()

## Summary
Severity: High
Contest weight: 0.6084
Dataset id: 12216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HegicOperationalTreasury contract provides an external lockLiquidityFor() function for privileged STRATEGY_ROLE to lock liquidity for an active option strategy. Our analysis with this routine shows its current implementation is not correct. To elaborate, we show below its code snippet. It comes to our attention that the state variable lockedPremium is not updated in the correct order. Specifically, the update for the state variable lockedPremium should precede the calculation of variable availableBalance (lines 91-92).
```solidity
* @notice
Used for locking liquidity in an active options strategy
* @param holder The option strategy holder address
* @param amount The amount of options strategy contract
* @param expiration The options strategy expiration time
function lockLiquidityFor(
    address holder,
    uint128 amount,
    uint32 expiration
) external override onlyRole(STRATEGY_ROLE) returns (uint256 optionID) {
    totalLocked += amount;
    uint128 premium = uint128(_addTokens());
    uint256 availableBalance = totalBalance + stakeandcoverPool.availableBalance() - lockedPremium;
    require(totalLocked <= availableBalance, "The amount is too large");
    require(block.timestamp + maxLockupPeriod >= expiration, "The period is too long");
    lockedPremium += premium;
    lockedByStrategy[msg.sender] += amount;
    optionID = manager.createOptionFor(holder);
    lockedLiquidity[optionID] = LockedLiquidity(
        LockedLiquidityState.Locked,
        msg.sender,
        amount,
        premium,
        expiration
    );
}
```

## Recommendation
Timely update the state variable lockedPremium.
