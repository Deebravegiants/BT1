### Title
Missing Access Control on `LRTOracle#updateRSETHPrice` Allows Anyone to Force Protocol Fee Minting and Trigger Protocol-Wide Pause — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a `public` function with no caller restriction. Any external account can invoke it at any time to update the rsETH price, mint protocol fees (rsETH) to the treasury, and — when the price has dropped below the configured threshold — trigger a protocol-wide pause that freezes all deposits and withdrawals.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no role check:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [1](#0-0) 

The internal `_updateRsETHPrice()` performs three security-sensitive operations that any unprivileged caller can trigger:

**1. Protocol fee minting (rsETH dilution)**

When `totalETHInProtocol > previousTVL`, the function computes a fee and mints rsETH to the treasury:

```solidity
// contracts/LRTOracle.sol L299-307
if (protocolFeeInETH > 0) {
    uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
    _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
    if (rsethAmountToMintAsProtocolFee > 0) {
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
        emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
    }
}
``` [2](#0-1) 

Any caller can force this fee mint at any time rewards have accrued, exhausting the daily fee minting limit (`maxFeeMintAmountPerDay`) and permanently blocking further fee collection for that 24-hour window.

**2. Daily fee limit exhaustion**

`_checkAndUpdateDailyFeeMintLimit` accumulates `currentPeriodMintedFeeAmount`. Once the limit is hit, all subsequent calls revert with `DailyFeeMintLimitExceeded`, preventing legitimate fee minting for the rest of the day:

```solidity
// contracts/LRTOracle.sol L205-209
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
currentPeriodMintedFeeAmount += feeAmount;
``` [3](#0-2) 

**3. Protocol-wide pause**

When the computed price drops below `pricePercentageLimit` relative to `highestRsethPrice`, the function pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` itself:

```solidity
// contracts/LRTOracle.sol L277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [4](#0-3) 

Any unprivileged caller can trigger this pause the moment the price condition is met, freezing all user deposits and withdrawals.

The privileged counterpart `updateRSETHPriceAsManager()` correctly restricts access:

```solidity
// contracts/LRTOracle.sol L94-96
function updateRSETHPriceAsManager() external onlyLRTManager {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The existence of this gated variant confirms the protocol authors intended privileged control over price updates in sensitive scenarios, yet left the primary entry point unrestricted.

---

### Impact Explanation

- **Permanent freezing of unclaimed yield (Medium)**: An attacker calls `updateRSETHPrice()` immediately after rewards accrue, exhausting `maxFeeMintAmountPerDay`. The protocol cannot collect further fees for the remainder of the 24-hour window. Repeated daily, this permanently suppresses protocol revenue.
- **Temporary freezing of funds (Medium)**: When market conditions cause the rsETH price to drop below the configured threshold, any attacker can call `updateRSETHPrice()` to pause `LRTDepositPool` and `LRTWithdrawalManager`, blocking all user deposits and withdrawals until an admin manually unpauses.

---

### Likelihood Explanation

The function is `public` with no authentication. Any EOA or contract can call it at zero cost beyond gas. The fee-minting path is triggered whenever rewards have accrued (a routine, predictable event). The pause path is triggered whenever price drops below threshold, a condition that can be monitored on-chain. Both paths are reliably reachable by an unprivileged attacker.

---

### Recommendation

Restrict `updateRSETHPrice()` to authorized callers (e.g., `onlyLRTOperator` or a dedicated keeper role), or split the function so that the fee-minting and pause-triggering logic is only reachable by privileged roles, while a permissionless variant is limited to pure price reads with no state-mutating side effects. The pattern already established by `updateRSETHPriceAsManager()` should be extended to cover the primary entry point.

---

### Proof of Concept

1. Rewards accrue in EigenLayer strategies, increasing `totalETHInProtocol` above `previousTVL * rsETHPrice`.
2. Attacker (any EOA) calls `LRTOracle.updateRSETHPrice()`.
3. `_updateRsETHPrice()` computes `protocolFeeInETH > 0`, mints rsETH to the treasury, and sets `currentPeriodMintedFeeAmount = maxFeeMintAmountPerDay`.
4. All subsequent legitimate calls to `updateRSETHPrice()` or `updateRSETHPriceAsManager()` that attempt to mint fees revert with `DailyFeeMintLimitExceeded` for the rest of the 24-hour window.
5. Alternatively: attacker monitors on-chain price. When `newRsETHPrice < highestRsethPrice` by more than `pricePercentageLimit`, attacker calls `updateRSETHPrice()`, triggering `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()`, freezing all user funds until admin intervention.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-209)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```
