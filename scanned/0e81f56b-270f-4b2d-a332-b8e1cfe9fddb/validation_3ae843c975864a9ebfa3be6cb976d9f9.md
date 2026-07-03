### Title
Missing Output Amount Validation in L2 Pool Deposit Functions Allows Zero rsETH Minting - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
All L2 deposit pool contracts share the same pattern: after computing `rsETHAmount` via `viewSwapRsETHAmountAndFee()`, the deposit functions proceed unconditionally without verifying that `rsETHAmount > 0`. Integer division can silently produce a zero output, causing the user to lose their deposited ETH or tokens while receiving nothing.

### Finding Description
In every L2 pool's `deposit()` function, the swap output is computed and immediately used without a zero-check:

```solidity
// RSETHPoolV3.sol – ETH deposit path
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);   // rsETHAmount can be 0
```

The calculation inside `viewSwapRsETHAmountAndFee` is:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;          // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate; // token path
```

Both are integer divisions. When `amountAfterFee` is small relative to `rsETHToETHrate`, the result truncates to zero. The same missing check exists identically in `RSETHPoolV3ExternalBridge.sol`, `RSETHPool.sol`, and `RSETHPoolNoWrapper.sol`.

The `limitDailyMint` modifier in `RSETHPoolV3.sol` and `RSETHPoolV3ExternalBridge.sol` also calls `viewSwapRsETHAmountAndFee` and adds the result to `dailyMintAmount`; a zero result does not revert, so the guard provides no protection.

By contrast, the L1 `LRTDepositPool.depositETH()` / `depositAsset()` correctly exposes a `minRSETHAmountExpected` parameter and reverts if `rsethAmountToMint < minRSETHAmountExpected`, giving users slippage protection that the L2 pools entirely lack.

### Impact Explanation
A depositor who sends a dust-sized ETH or token amount (e.g., 1 wei) receives 0 rsETH while the pool retains the deposited asset. The deposited value is permanently lost to the user. This matches the allowed impact category: **"Contract fails to deliver promised returns, but doesn't lose value"** (Low).

### Likelihood Explanation
The zero-output condition is triggered by very small deposit amounts (on the order of 1 wei for ETH, or a few units for low-value tokens). While accidental occurrence is rare, the absence of any minimum-output guard means the contract silently accepts and finalises such transactions with no revert. Any user who sends a dust deposit — whether by mistake or through a buggy integration — suffers the loss with no on-chain protection.

### Recommendation
Add an explicit zero-output guard in every L2 pool `deposit()` function, mirroring the L1 pattern:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, expose a `minRsETHAmountExpected` parameter (as `LRTDepositPool` does) so callers can enforce their own slippage tolerance.

### Proof of Concept
1. `rsETHToETHrate` is, say, `1.05e18` (rsETH worth 1.05 ETH).
2. User calls `RSETHPoolV3.deposit{value: 1}("")` (1 wei ETH, `feeBps = 0`).
3. `viewSwapRsETHAmountAndFee(1)` computes `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation).
4. `wrsETH.mint(msg.sender, 0)` is called — user receives nothing.
5. The 1 wei ETH is retained by the pool as `feeEarnedInETH` is unchanged; the ETH is effectively lost. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L258-263)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L377-384)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L271-278)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L237-243)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
