# [M] Bringing a position from unsafe to safe by liquidation paritally

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-07-loopfi
Published: 2024-10-14
Source: https://github.com/code-423n4/2024-07-loopfi-findings/issues/571
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-loopfi/blob/57871f64bdea450c1f04c9a53dc1a78223719164/src/CDPVault.sol#L509


# Vulnerability details


## Impact

The CDPVault's liquidation mechanism allows partial liquidations to temporarily bring unsafe positions back to a safe state. This can delay necessary liquidations if collateral prices continue to fall, potentially leading to increased risk and larger losses for the protocol. 

## Proof of Concept

The issue arises from `liquidatePosition` function in the CDPVault contract. An attacker can exploit this to avoid full liquidation even when their position should be unsafe.

**Break down the Scenario:**
- Alice creates a position with 100 ether collateral and 60 ether debt.
- The collateral price drops, making Alice's position unsafe.
- Bob performs a partial liquidation on Alice's position.
- Alice's position becomes temporarily safe due to the partial liquidation.
- The collateral price drops further, but a small liquidation attempt by Carol fails because the position is still considered safe.
- Only after an even further price drop can the position be liquidated again.

Alice can do the same flow to herself (self liqudation) to protect her position instead of maintaining it by increasing the colleteral, which costs less and goes against how the protocol is intended to work.

[at function liquidatePosition](https://github.com/code-423n4/2024-07-loopfi/blob/57871f64bdea450c1f04c9a53dc1a78223719164/src/CDPVault.sol#L509)

```solidity
function liquidatePosition(address owner, uint256 repayAmount) external whenNotPaused {
    // ... (validation and state loading)
    if (_isCollateralized(calcTotalDebt(debtData), wmul(position.collateral, spotPrice_), config.liquidationRatio))
        revert CDPVault__liquidatePosition_notUnsafe();
    // ... (liquidation calculations)
    position = _modifyPosition(owner, position, newDebt, newCumulativeIndex, -toInt256(takeCollateral), totalDebt);
    // ... (state updates and transfers)
}
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-07-loopfi-findings/issues/571_
