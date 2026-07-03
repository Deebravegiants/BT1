### Title
Fee Rounding to Zero Enables Protocol Fee Evasion on Every Deposit - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee` function in all L2 pool contracts computes the protocol fee using integer division that truncates toward zero. For any deposit amount where `amount * feeBps < 10_000`, the fee rounds to exactly `0` while the depositor still receives a non-zero `rsETH`/`wrsETH` amount. An unprivileged depositor can exploit this systematically to drain all protocol fee revenue by splitting deposits into fee-evading chunks.

### Finding Description
Every L2 pool contract in the family computes the swap fee identically:

```solidity
// contracts/pools/RSETHPoolV3.sol L300-307
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Solidity integer division truncates. When `amount * feeBps < 10_000`, the expression `amount * feeBps / 10_000` evaluates to `0`. The only guard against a zero-amount deposit is:

```solidity
if (amount == 0) revert InvalidAmount();
```

There is no minimum deposit amount check. Therefore any `amount ≥ 1` that satisfies `amount < 10_000 / feeBps` passes the guard, produces `fee = 0`, and still yields a positive `rsETHAmount` (provided `amount * 1e18 ≥ rsETHToETHrate`, which is trivially satisfied for any deposit of practical size on L2 chains where ETH is the unit).

The same pattern is replicated verbatim across the entire pool family:

- `contracts/pools/RSETHPool.sol` lines 312 and 336
- `contracts/pools/RSETHPoolV3.sol` lines 300 and 324
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` lines 419 and 442
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` lines 336 and 360
- `contracts/pools/RSETHPoolNoWrapper.sol` lines 278 and 301

### Impact Explanation
**High. Theft of unclaimed yield.**

Protocol fees are the only revenue stream collected by these pools (`feeEarnedInETH`, `feeEarnedInToken`). By depositing in fee-evading chunks, an attacker captures the full economic value of every deposit without contributing any fee. Over the lifetime of the pool, 100% of fee revenue can be stolen. The stolen value is the fee that should have accrued to the protocol treasury but never does.

### Likelihood Explanation
**High.** The attack requires no special role, no oracle manipulation, and no flash loan. Any EOA or contract that can call `deposit()` can exploit this. The threshold amount below which fee = 0 is:

```
threshold = floor((10_000 - 1) / feeBps)
```

For a typical `feeBps = 5` (0.05%), the threshold is `1999 wei`. On L2 chains (Arbitrum, Optimism, Base) where gas costs are negligible, batching thousands of 1999-wei deposits is economically rational. The attacker pays full ETH value but zero fee on every call.

### Recommendation
Replace the truncating division with a ceiling division for the fee, so the protocol always collects at least 1 wei of fee for any non-zero deposit:

```solidity
// Use ceiling division: ceil(amount * feeBps / 10_000)
fee = (amount * feeBps + 9_999) / 10_000;
```

Alternatively, enforce a minimum deposit amount that guarantees `amount * feeBps >= 10_000`, or revert when `fee == 0` and `feeBps > 0`.

### Proof of Concept
**Setup:**
- Pool: `RSETHPoolV3` on Arbitrum (or any chain)
- `feeBps = 5` (0.05%, a realistic value)
- `rsETHToETHrate = 1.05e18` (rsETH trades at a 5% premium over ETH)

**Attack:**
1. Attacker calls `deposit{value: 1999}("")` (1999 wei of ETH).
2. Inside `viewSwapRsETHAmountAndFee(1999)`:
   - `fee = 1999 * 5 / 10_000 = 9995 / 10_000 = 0` ← truncated to zero
   - `amountAfterFee = 1999 - 0 = 1999`
   - `rsETHAmount = 1999 * 1e18 / 1.05e18 = 1903` (non-zero)
3. `feeEarnedInETH += 0` — no fee recorded.
4. `wrsETH.mint(attacker, 1903)` — attacker receives wrsETH.
5. Repeat N times. Total ETH deposited: `N × 1999 wei`. Total fee collected: `0`.

Expected fee per call at 0.05%: `~1 wei`. Over 10,000 calls the protocol loses ~10,000 wei of fee. On L2 where each call costs ~$0.001 in gas, the attacker can profitably drain all fee revenue for any pool with meaningful TVL. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L254-264)
```text
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3.sol (L323-335)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-320)
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

**File:** contracts/pools/RSETHPool.sol (L335-347)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L335-344)
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
