The code confirms all claims. Let me verify the key elements:

1. `_checkAndUpdateDailyFeeMintLimit` reverts unconditionally when cap exceeded — confirmed at lines 205–207. [1](#0-0) 

2. `rsETHPrice = newRsETHPrice` is placed **after** the fee check — confirmed at line 313 vs line 303. [2](#0-1) 

3. Both public entry points call `_updateRsETHPrice()` — confirmed at lines 87–96. [3](#0-2) 

4. Depositors divide by `lrtOracle.rsETHPrice()` — confirmed at line 520. [4](#0-3) 

---

Audit Report

## Title
Daily Fee Mint Cap Reverts `_updateRsETHPrice`, Freezing `rsETHPrice` for Up to 24 Hours - (File: contracts/LRTOracle.sol)

## Summary
In `LRTOracle.sol`, `_updateRsETHPrice()` calls `_checkAndUpdateDailyFeeMintLimit()` before writing `rsETHPrice = newRsETHPrice`. When `currentPeriodMintedFeeAmount + rsethAmountToMintAsProtocolFee > maxFeeMintAmountPerDay`, the function reverts with `DailyFeeMintLimitExceeded`, leaving `rsETHPrice` frozen at its stale value for up to 24 hours. Both public entry points (`updateRSETHPrice()` and `updateRSETHPriceAsManager()`) share this path, so neither can update the price until the period resets or an admin raises the cap.

## Finding Description
In `_updateRsETHPrice()` (LRTOracle.sol L214–316), the price write `rsETHPrice = newRsETHPrice` at line 313 is placed after `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` at line 303. `_checkAndUpdateDailyFeeMintLimit()` (L197–210) unconditionally reverts with `DailyFeeMintLimitExceeded` when `currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay`. The period only resets when `block.timestamp >= feePeriodStartTime + 1 days` (L199), so the revert persists for up to 24 hours. The `else` branch at line 310 also calls `_checkAndUpdateDailyFeeMintLimit(0)`, which passes the cap check (0 never exceeds the limit), so zero-fee updates are unaffected — but any TVL-growth update that generates a non-zero fee is blocked. Both `updateRSETHPrice()` (L87–89, public) and `updateRSETHPriceAsManager()` (L94–96, manager-only) call `_updateRsETHPrice()` and are equally blocked. The only on-chain mitigation is for the LRT manager to call `setMaxFeeMintAmountPerDay()` to raise the cap, requiring active human intervention within the freeze window.

## Impact Explanation
While `rsETHPrice` is frozen at a stale (lower-than-current) value, `LRTDepositPool.getRsETHAmountToMint()` computes `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()` (L520). Dividing by a stale lower price causes new depositors to receive more rsETH than they are entitled to, diluting existing holders' accrued yield. This constitutes theft of unclaimed yield from existing rsETH holders (embedded in the price appreciation) and a temporary functional freeze of the oracle, matching **Medium: Temporary freezing of funds** as claimed, with characteristics also consistent with **High: Theft of unclaimed yield**.

## Likelihood Explanation
The condition is reachable through normal protocol operation without any attacker. As TVL grows throughout a day (staking rewards, new deposits), each successful `updateRSETHPrice()` call increments `currentPeriodMintedFeeAmount`. Once the running total approaches `maxFeeMintAmountPerDay`, the next fee-generating update reverts. No privileged access, no victim mistake, and no external dependency is required — any caller of the public `updateRSETHPrice()` will trigger the revert once the cap is reached, and the freeze persists until the 24-hour period resets.

## Recommendation
Decouple the price write from the fee-mint check. Move `rsETHPrice = newRsETHPrice` before `_checkAndUpdateDailyFeeMintLimit()`. If the cap is exceeded, skip or clamp the fee mint (emit an event) but still commit the updated price. This ensures the price oracle is never blocked by the fee accounting subsystem.

## Proof of Concept
```solidity
// Foundry fork test outline:
// 1. Deploy/fork with maxFeeMintAmountPerDay = 1e18
// 2. Simulate prior updates: set currentPeriodMintedFeeAmount = 0.99e18
//    (via multiple updateRSETHPrice() calls or direct storage manipulation in test)
// 3. Increase TVL by 0.02e18 worth of rewards (so fee would be ~0.02e18 rsETH)
// 4. Call updateRSETHPrice() → expect revert DailyFeeMintLimitExceeded
// 5. Assert rsETHPrice == stalePriceFromLastUpdate (unchanged)
// 6. Call updateRSETHPriceAsManager() as LRT manager → also reverts
// 7. Advance time by < 1 day → still reverts
// 8. Advance time past feePeriodStartTime + 1 days → updateRSETHPrice() succeeds
// 9. During freeze window: call depositAsset() and assert rsethAmountToMint
//    is greater than it would be at the correct (higher) price,
//    confirming dilution of existing holders.
```

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-207)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```

**File:** contracts/LRTOracle.sol (L303-313)
```text
            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
