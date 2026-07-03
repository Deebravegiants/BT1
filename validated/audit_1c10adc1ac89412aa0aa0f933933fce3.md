### Title
Fee Calculation Integer Truncation to Zero Allows Fee-Free Deposits for Small Amounts — (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee` function in all L2 pool variants computes the protocol fee using integer division `fee = amount * feeBps / 10_000`. When `amount * feeBps < 10_000`, Solidity's integer division truncates the result to zero. This is the direct structural analog to the SHA256 `partial_sha256_var_start` bug: just as `num_blocks = N / BLOCK_SIZE` evaluates to zero for small `N` and causes the hash loop to be entirely skipped — returning the same initial state for all small inputs — here the fee division evaluates to zero for small deposits, causing the fee deduction step to be entirely skipped and returning the same fee (zero) for all deposits below the truncation threshold.

### Finding Description
In `RSETHPoolV3.viewSwapRsETHAmountAndFee` (and identically in `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`), the fee is computed as:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

When `amount * feeBps < 10_000`, `fee` truncates to zero. `amountAfterFee` then equals the full `amount`, and the user receives rsETH calculated on the full deposit with no fee deducted. The protocol's `feeEarnedInETH` (or `feeEarnedInToken`) accumulator is incremented by zero.

Concrete threshold examples:
- `feeBps = 10` (0.1%): any `amount < 1000 wei` → `fee = 0`
- `feeBps = 100` (1%): any `amount < 100 wei` → `fee = 0`
- `feeBps = 1000` (10%, the maximum allowed): any `amount < 10 wei` → `fee = 0`

The `deposit()` functions only guard against `amount == 0`; there is no minimum deposit enforced in the L2 pool contracts. [1](#0-0) [2](#0-1) 

The same truncation pattern is replicated verbatim across every pool variant: [3](#0-2) [4](#0-3) 

The `limitDailyMint` modifier also calls `viewSwapRsETHAmountAndFee` to compute the rsETH amount to track against the daily cap. When `fee = 0` due to truncation, `dailyMintAmount` is incremented by a slightly inflated rsETH value (computed on the full amount rather than amount minus fee), causing a marginal over-consumption of the daily mint budget — but this is a secondary effect. [5](#0-4) 

### Impact Explanation
For any deposit where `amount * feeBps < 10_000`, the protocol collects zero fee and mints rsETH based on the full deposit amount. The intended fee revenue is silently lost. The rsETH minted is fractionally over-valued relative to the ETH actually contributed net of fees. This constitutes the protocol failing to deliver its promised fee-collection behavior. Impact: **Low — Contract fails to deliver promised returns, but doesn't lose value** (fee revenue is foregone, not stolen from existing holders in a material way).

### Likelihood Explanation
Low. On L2 networks (Arbitrum, Base, Optimism, Scroll, Linea, Unichain), gas costs per transaction are orders of magnitude larger than the fee savings achievable by depositing below the truncation threshold. For example, saving 1 wei of fee on a 99-wei deposit is economically irrational when the transaction costs thousands of wei in gas. The bug is structurally present and reachable by any depositor, but rational actors have no incentive to exploit it at scale.

### Recommendation
Replace the truncating integer division with a rounding-up fee calculation, or enforce a minimum deposit amount in the L2 pool contracts that guarantees `amount * feeBps >= 10_000` for any non-zero `feeBps`. For example:

```solidity
// Round fee up to avoid truncation to zero
fee = (amount * feeBps + 9_999) / 10_000;
```

Alternatively, add a minimum deposit guard analogous to `minAmountToDeposit` in `LRTDepositPool`: [6](#0-5) 

### Proof of Concept
1. Deploy `RSETHPoolV3` with `feeBps = 100` (1%).
2. Call `deposit{value: 99}("")` — passes the `amount == 0` guard.
3. `viewSwapRsETHAmountAndFee(99)` computes `fee = 99 * 100 / 10_000 = 0`.
4. `amountAfterFee = 99`, `rsETHAmount = 99 * 1e18 / rsETHToETHrate`.
5. `feeEarnedInETH += 0` — protocol collects no fee.
6. User receives rsETH equivalent to the full 99 wei deposit with no fee deducted.
7. Repeat for any `amount ∈ [1, 99]` — all produce `fee = 0`, identical to a zero-fee deposit. [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L254-256)
```text
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();
```

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

**File:** contracts/LRTDepositPool.sol (L657-659)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }
```
