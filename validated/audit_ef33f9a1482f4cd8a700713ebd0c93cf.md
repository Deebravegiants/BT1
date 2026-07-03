Audit Report

## Title
Stale `rsETHPrice` in `LRTOracle` Used in Deposit Mint Calculation Allows Excess rsETH Minting - (File: `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

## Summary

`LRTOracle.rsETHPrice` is a cached state variable updated only via a standalone `updateRSETHPrice()` call. `LRTDepositPool.getRsETHAmountToMint()` reads this cached value directly without refreshing it. When staking rewards accrue and the true rsETH price rises before `updateRSETHPrice()` is called, depositors receive more rsETH than their deposit warrants, diluting existing holders' accrued yield.

## Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a persistent state variable:

```solidity
uint256 public override rsETHPrice;
``` [1](#0-0) 

This value is only updated when `updateRSETHPrice()` is called as a standalone transaction:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [2](#0-1) 

`_updateRsETHPrice()` computes `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply` from live on-chain balances and writes it to `rsETHPrice` only at the end of the function: [3](#0-2) 

In `LRTDepositPool`, both `depositETH()` and `depositAsset()` call `_beforeDeposit()`, which calls `getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [4](#0-3) 

`lrtOracle.rsETHPrice()` reads the **cached storage value**. There is no call to `updateRSETHPrice()` anywhere in the deposit flow (`depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint`): [5](#0-4) 

An additional complication: `_updateRsETHPrice()` enforces a `pricePercentageLimit` check that **reverts for non-manager callers** if the price increase exceeds the threshold:

```solidity
if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
    revert PriceAboveDailyThreshold();
}
``` [6](#0-5) 

This means that when rewards push the price above the threshold, only a manager can update it — extending the stale window and making the vulnerability more exploitable.

**Mathematical proof of profit:**

Let V = true TVL (post-rewards), V_old = cached TVL (pre-rewards), S = rsETH supply, D = deposit value.

- Attacker mints: `rsETH_minted = D * S / V_old`
- After price update, new price = `(V + D) / (S + D*S/V_old)`
- Attacker's ETH value on redemption = `D * (V + D) / (V_old + D)`
- Since V > V_old: attacker's value > D, profit = `D * (V - V_old) / (V_old + D)`

The excess comes directly from the yield that should have accrued to existing rsETH holders.

## Impact Explanation

**High — Theft of unclaimed yield.** An attacker who deposits during the stale-price window receives more rsETH than the deposited value justifies. When `updateRSETHPrice()` is eventually called, the attacker's rsETH represents a larger share of the protocol's TVL than they paid for. On redemption via the withdrawal manager, they extract more ETH than they deposited. The excess is the yield that should have accrued to existing rsETH holders.

## Likelihood Explanation

EigenLayer staking rewards accrue continuously. Every block between a reward accrual event and the next `updateRSETHPrice()` call creates a stale-price window. The `pricePercentageLimit` guard can block permissionless updates when the price gap is large (e.g., after a large reward distribution), widening the window to potentially hours or days. An attacker can monitor on-chain balances to detect when `rsETHPrice` is stale and deposit opportunistically. No special privileges are required — only a standard `depositAsset()` or `depositETH()` call.

## Recommendation

Call `_updateRsETHPrice()` (or an equivalent inline computation) atomically at the start of `depositAsset()` and `depositETH()` before computing `rsethAmountToMint`, so the mint calculation always uses the freshly computed price. Alternatively, replace `lrtOracle.rsETHPrice()` in `getRsETHAmountToMint()` with a live computation equivalent to `_getTotalEthInProtocol() / rsethSupply` to avoid relying on the cached storage value.

## Proof of Concept

1. At time T, `rsETHPrice = 1.00e18` (cached). EigenLayer rewards accrue, making the true price `1.01e18`. `updateRSETHPrice()` has not been called (or is blocked by `pricePercentageLimit` for non-managers).
2. Attacker calls `depositAsset(stETH, 100e18, 0, "")`.
3. `getRsETHAmountToMint` computes: `100e18 * 1e18 / 1.00e18 = 100e18 rsETH` (correct amount at true price would be `~99.01e18 rsETH`).
4. Attacker receives `~0.99e18` excess rsETH.
5. Manager calls `updateRSETHPrice()`. New price reflects the attacker's dilution of existing holders.
6. Attacker redeems `100e18 rsETH` via the withdrawal manager for `~101 ETH`, extracting `~1 ETH` profit at the expense of existing rsETH holders.

**Foundry fork test plan:**
- Fork mainnet at a block where EigenLayer rewards have accrued since the last `updateRSETHPrice()` call.
- Record `rsETHPrice` and compute the true price via `_getTotalEthInProtocol() / rsethSupply`.
- Call `depositAsset()` as an unprivileged attacker and record rsETH minted.
- Call `updateRSETHPrice()` as manager.
- Verify attacker's rsETH redeems for more ETH than deposited, with the difference sourced from existing holders' yield.

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-313)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
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

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```
