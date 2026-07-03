### Title
Protocol Treasury Fee Not Minted When Emergency Price-Decrease Pause Triggers Early Return — (File: contracts/LRTOracle.sol)

### Summary

In `LRTOracle._updateRsETHPrice()`, when the computed new rsETH price falls below the historical peak by more than `pricePercentageLimit` (`isPriceDecreaseOffLimit == true`), the function pauses the protocol and **returns early** before minting the protocol fee to the treasury. If the TVL had increased since the last update (making `protocolFeeInETH > 0`), that fee is computed, subtracted from the price numerator, but never actually minted. The subsequent manager-only price update runs with `protocolPaused == true`, so the fee is not recomputed, and the treasury permanently loses it.

### Finding Description

`_updateRsETHPrice()` computes `protocolFeeInETH` whenever `!protocolPaused && totalETHInProtocol > previousTVL`: [1](#0-0) 

It then computes `newRsETHPrice` with the fee already subtracted from the numerator: [2](#0-1) 

Immediately after, the downside-protection block checks whether the new price is too far below `highestRsethPrice`. If so, it pauses the protocol and **returns early**: [3](#0-2) 

The fee-minting block that sends rsETH to the treasury is never reached: [4](#0-3) 

After the early return, `paused == true` on the oracle. The next call to `_updateRsETHPrice` (only possible via the manager-only `updateRSETHPriceAsManager`) re-evaluates: [5](#0-4) 

Because `paused == true`, `protocolPaused == true`, so `protocolFeeInETH` is forced to `0` again. The fee from the previous period is permanently unrecoverable.

### Impact Explanation

The protocol treasury (`PROTOCOL_TREASURY`) permanently loses the rsETH fee that was earned during the TVL-increase period immediately before the emergency pause. This is **permanent freezing / theft of unclaimed yield** (treasury yield that was earned but never distributed). Severity: **Medium** (permanent freezing of unclaimed yield).

### Likelihood Explanation

The scenario requires three simultaneous conditions:
1. `pricePercentageLimit > 0` (configured by admin — normal operational state).
2. `totalETHInProtocol > previousTVL` (TVL increased since last update — e.g., staking rewards accrued).
3. `newRsETHPrice` (after fee deduction) is still more than `pricePercentageLimit` below `highestRsethPrice` — realistic during price recovery after a slashing event where the all-time-high price is significantly above the current recovery level.

This combination is realistic in any post-slashing recovery period and requires no attacker action — it is triggered by the normal `updateRSETHPrice()` call (callable by anyone).

### Recommendation

Before executing the early return, mint any already-computed `protocolFeeInETH` to the treasury:

```solidity
if (isPriceDecreaseOffLimit) {
    // Mint any earned fee before pausing
    if (protocolFeeInETH > 0) {
        uint256 feeToMint = protocolFeeInETH.divWad(newRsETHPrice);
        _checkAndUpdateDailyFeeMintLimit(feeToMint);
        if (feeToMint > 0) {
            address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
            IRSETH(rsETHTokenAddress).mint(treasury, feeToMint);
            emit FeeMinted(treasury, feeToMint);
        }
    }
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

### Proof of Concept

1. `highestRsethPrice = 1.1e18` (set during a previous peak).
2. A slashing event drops TVL; `rsETHPrice` is updated to `0.75e18`. `pricePercentageLimit = 0.05e18` (5%).
3. Staking rewards accrue: `totalETHInProtocol` rises slightly above `previousTVL`.
4. Anyone calls `updateRSETHPrice()`.
5. `protocolFeeInETH > 0` is computed (TVL increased).
6. `newRsETHPrice ≈ 0.76e18` — still `(1.1 - 0.76)/1.1 ≈ 31%` below `highestRsethPrice`, exceeding the 5% limit.
7. `isPriceDecreaseOffLimit == true` → protocol pauses, function returns early.
8. Fee is never minted. Manager calls `updateRSETHPriceAsManager()` → `protocolPaused == true` → `protocolFeeInETH = 0` → fee permanently lost. [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L240-247)
```text
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```
