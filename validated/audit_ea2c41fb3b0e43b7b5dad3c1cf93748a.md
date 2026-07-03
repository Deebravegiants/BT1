Audit Report

## Title
`LRTOracle.updateRSETHPrice()` DoS via shared `RSETH.checkDailyMintLimit` counter exhausted by user deposits - (File: contracts/LRTOracle.sol)

## Summary

`RSETH.mint()` enforces a single shared `checkDailyMintLimit` modifier that increments `currentPeriodMintedAmount` for every caller — both user deposits via `LRTDepositPool._mintRsETH()` and protocol-fee minting via `LRTOracle._updateRsETHPrice()`. When ordinary depositors exhaust `maxMintAmountPerDay`, the fee-mint call inside `_updateRsETHPrice()` reverts, making `updateRSETHPrice()` uncallable for the remainder of the 24-hour window and leaving `rsETHPrice` stale.

## Finding Description

`LRTOracle._updateRsETHPrice()` computes a protocol fee and mints it via `IRSETH.mint()`: [1](#0-0) 

Although `LRTOracle` maintains its own separate fee-mint accounting (`currentPeriodMintedFeeAmount`, `feePeriodStartTime`, `maxFeeMintAmountPerDay`) checked by `_checkAndUpdateDailyFeeMintLimit`: [2](#0-1) 

...the actual `IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee)` call at line 306 still routes through `RSETH.mint()`, which unconditionally applies the `checkDailyMintLimit` modifier: [3](#0-2) 

That modifier checks and increments the **global** `currentPeriodMintedAmount` counter: [4](#0-3) 

`LRTDepositPool._mintRsETH()` calls the exact same `RSETH.mint()` for every user deposit: [5](#0-4) 

Both paths share the single `currentPeriodMintedAmount` counter. Once user deposits push it to `maxMintAmountPerDay`, the oracle's subsequent `RSETH.mint()` call hits `DailyMintLimitExceeded`, the revert propagates through `_updateRsETHPrice()`, and `updateRSETHPrice()` (the sole public price-refresh entry point) becomes uncallable: [6](#0-5) 

The oracle's own `_checkAndUpdateDailyFeeMintLimit` guard is insufficient because it operates on a separate counter and does not prevent the downstream `RSETH.mint()` from reverting on the shared RSETH-level counter.

## Impact Explanation

`rsETHPrice` is not updated for the remainder of the 24-hour window. Every subsequent call to `getRsETHAmountToMint` reads the stale price, causing depositors to receive incorrect rsETH amounts. This constitutes **Low — contract fails to deliver promised returns** (incorrect exchange rate without direct fund loss), with a secondary argument for **Medium — temporary freezing of funds** if the stale price is considered to temporarily impair fair rsETH issuance and withdrawal valuation.

## Likelihood Explanation

`updateRSETHPrice()` is a permissionless public function. Any combination of depositors that collectively reaches `maxMintAmountPerDay` triggers the condition. Depositors receive rsETH in return, so the cost is only opportunity cost of capital. On a chain with high deposit activity or a conservatively set `maxMintAmountPerDay`, this is reachable without any special privilege and is repeatable every 24-hour window.

## Recommendation

Decouple the oracle's fee-minting path from the user-deposit mint counter. Two concrete options:

1. Add a separate `mintFee(address to, uint256 amount)` function to `RSETH` with its own independent daily counter (or no counter), callable only by `LRTOracle`, so exhausting the user-deposit cap cannot block fee minting.
2. Wrap the `IRSETH.mint(treasury, ...)` call in `_updateRsETHPrice()` with a try/catch on `DailyMintLimitExceeded`: skip the fee mint for that period but continue to update `rsETHPrice`, preventing the DoS while deferring the fee.

## Proof of Concept

1. `RSETH.maxMintAmountPerDay` is set to some finite value `M`.
2. Depositors call `LRTDepositPool.depositETH{value: X}()` repeatedly until `currentPeriodMintedAmount == M`. Each call routes through `_mintRsETH → RSETH.mint → checkDailyMintLimit`, incrementing the shared counter.
3. TVL has grown since the last price update, so `protocolFeeInETH > 0` when `updateRSETHPrice()` is next called.
4. `_updateRsETHPrice()` passes its own `_checkAndUpdateDailyFeeMintLimit` check (separate counter), then calls `IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee)`.
5. `RSETH.mint` executes `checkDailyMintLimit`: `currentPeriodMintedAmount + fee > M` → `revert DailyMintLimitExceeded(...)`.
6. Revert bubbles up; `updateRSETHPrice()` reverts. `rsETHPrice` is not updated for the rest of the 24-hour window.
7. All subsequent deposits use the stale price, minting incorrect rsETH amounts.

### Citations

**File:** contracts/LRTOracle.sol (L32-35)
```text
    // Daily fee minting limit variables
    uint256 public currentPeriodMintedFeeAmount;
    uint256 public feePeriodStartTime;
    uint256 public maxFeeMintAmountPerDay;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
