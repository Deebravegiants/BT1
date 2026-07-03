### Title
Fee Calculations Round Down in Favor of Depositors, Leaking Protocol Revenue - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/LRTWithdrawalManager.sol, contracts/LRTOracle.sol)

---

### Summary

Across all L2 pool contracts and the L1 withdrawal manager, fee calculations use plain integer division (`/`) which rounds down in Solidity. This means the protocol and fee recipients collect slightly less than the mathematically correct fee on every swap and instant withdrawal. The same pattern appears in the L1 oracle's protocol fee computation. This is the direct analog of the Sudoswap rounding-direction bug: fees should round up to prevent value leaking from the system to traders.

---

### Finding Description

Every `viewSwapRsETHAmountAndFee` implementation across the pool family computes the fee as:

```solidity
fee = amount * feeBps / 10_000;          // integer division → rounds DOWN
uint256 amountAfterFee = amount - fee;   // slightly larger than intended
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // also rounds DOWN
```

Because `fee` is rounded down, `amountAfterFee` is rounded up by the same 0–1 wei, and the user receives slightly more rsETH than the exact rate warrants. The protocol's `feeEarnedInETH` / `feeEarnedInToken` accumulates a value that is up to 1 wei short per transaction.

The same pattern appears in `LRTWithdrawalManager.instantWithdrawal`:

```solidity
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;  // rounds DOWN
uint256 userAmount = assetAmountUnlocked - fee;                        // rounds UP
```

And in `LRTOracle._updateRsETHPrice`:

```solidity
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;  // rounds DOWN
```

Affected files and lines:

| File | Line(s) |
|---|---|
| `contracts/pools/RSETHPoolV3.sol` | 300, 324 |
| `contracts/pools/RSETHPoolNoWrapper.sol` | 278, 301 |
| `contracts/pools/RSETHPoolV2ExternalBridge.sol` | 308 |
| `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` | 336, 360 |
| `contracts/LRTWithdrawalManager.sol` | 237 |
| `contracts/LRTOracle.sol` | 246 |

---

### Impact Explanation

On every deposit the protocol collects up to 1 wei less fee than it should, and the depositor receives up to 1 wei more rsETH than the exact rate warrants. Over a high volume of transactions this constitutes a systematic, if small, revenue leak from the protocol to depositors. The instant-withdrawal fee and the oracle protocol fee suffer the same truncation. No user funds are at risk of theft; the protocol simply fails to collect the exact fee it is entitled to.

**Severity: Low** — Contract fails to deliver promised returns (exact fee revenue), but no value is lost from user balances.

---

### Likelihood Explanation

This is triggered on every single deposit and instant withdrawal — no special conditions are required. Any unprivileged depositor calling `deposit()` or `instantWithdrawal()` exercises the vulnerable path. Likelihood is **High** (it fires on every interaction), but the per-transaction loss is bounded at 1 wei, keeping overall severity Low.

---

### Recommendation

Replace plain division with a ceiling-division helper for fee calculations so that fees always round up:

```solidity
// Instead of:
fee = amount * feeBps / 10_000;

// Use (mulDiv with Rounding.Up, or an inline ceiling):
fee = Math.mulDiv(amount, feeBps, 10_000, Math.Rounding.Up);
```

Apply the same fix to `instantWithdrawalFee` in `LRTWithdrawalManager` and to `protocolFeeInBPS` in `LRTOracle._updateRsETHPrice`.

---

### Proof of Concept

Consider a deposit of `amount = 10_001 wei` with `feeBps = 3` (0.03 %):

```
Exact fee  = 10_001 × 3 / 10_000 = 3.0003 wei
Rounded-down fee (current) = 3 wei
amountAfterFee = 10_001 − 3 = 9_998 wei   (should be 9_997.9997)
```

The user receives rsETH computed on 9,998 wei instead of 9,997.9997 wei. The protocol's `feeEarnedInETH` records 3 wei instead of the correct 3.0003 wei. Repeated across millions of transactions the shortfall accumulates. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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

**File:** contracts/LRTWithdrawalManager.sol (L237-238)
```text
        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```
