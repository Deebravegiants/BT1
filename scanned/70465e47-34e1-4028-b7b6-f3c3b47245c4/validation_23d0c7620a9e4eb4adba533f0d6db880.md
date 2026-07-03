### Title
Rounding Down in Fee Calculation Allows Fee-Free Deposits - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The fee calculation in every L2 pool contract uses plain integer division that truncates toward zero. For deposit amounts below the fee-rounding threshold, the computed fee is exactly 0, meaning the depositor pays no protocol fee while still receiving the full rsETH/wrsETH output. This is the direct structural analog of the Caviar `buyQuote` rounding bug: the incoming asset owed to the protocol (the fee) is computed with a floor division, allowing it to silently collapse to zero.

### Finding Description
In all pool variants the fee is computed identically:

```solidity
// RSETHPoolV3.sol – ETH path
fee = amount * feeBps / 10_000;          // line 300
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // line 307

// RSETHPoolV3.sol – token path
fee = amount * feeBps / 10_000;          // line 324
```

Solidity integer division truncates toward zero. Whenever `amount * feeBps < 10_000`, the expression evaluates to 0. The user then receives rsETH/wrsETH calculated on the full `amount` (since `amountAfterFee = amount − 0 = amount`), paying zero fee.

The identical pattern is present in:
- `RSETHPoolV3.sol` lines 300 and 324
- `RSETHPoolV3ExternalBridge.sol` lines 419 and 442
- `RSETHPool.sol` lines 312 and 336
- `RSETHPoolNoWrapper.sol` lines 278 and 301
- `RSETHPoolV3WithNativeChainBridge.sol` lines 336 and 360 [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

### Impact Explanation
The fee is the yield that accrues to the protocol and its LP holders. When the fee truncates to zero, the protocol delivers fewer promised returns than the configured `feeBps` implies. Any deposit whose size falls below the rounding threshold silently bypasses the fee entirely. Repeated small deposits accumulate this shortfall. The impact maps to **Low – contract fails to deliver promised returns** (fee income is lower than configured), with a secondary framing as **High – theft of unclaimed yield** if the cumulative shortfall is considered over many deposits. Per-transaction the stolen amount is at most 1 wei of fee, but the structural defect is identical to the Caviar bug: the incoming asset owed to the protocol is rounded in the depositor's favor.

### Likelihood Explanation
Any unprivileged depositor triggers this automatically whenever their deposit falls below the threshold. For `feeBps = 5` (0.05 %), the threshold is `amount < 2 000 wei`; for `feeBps = 30` (0.3 %), it is `amount < 334 wei`. On L2 chains (Arbitrum, Optimism, Base, Linea, Unichain) gas costs are low but still far exceed the per-transaction fee saved, making deliberate exploitation economically irrational. However, organic micro-deposits (e.g., dust amounts, automated rebalancers) will naturally hit this path and incur zero fee without any attacker intent.

### Recommendation
Round the fee **up** so the protocol always collects at least 1 wei when `feeBps > 0`. OpenZeppelin's `Math.mulDiv` with `Rounding.Up` is already available in the dependency tree:

```solidity
import { Math } from "@openzeppelin/contracts/utils/math/Math.sol";

// Replace in every pool's viewSwapRsETHAmountAndFee:
fee = Math.mulDiv(amount, feeBps, 10_000, Math.Rounding.Up);
```

This mirrors the fix recommended in the Caviar report (use `mulDivUp` so the required incoming amount is always at least 1 wei).

### Proof of Concept
Concrete example using `RSETHPoolV3` with `feeBps = 5`:

| Variable | Value |
|---|---|
| `feeBps` | 5 (0.05 %) |
| `amount` | 1 999 wei |
| `amount * feeBps` | 9 995 |
| `fee = 9995 / 10_000` | **0** (truncated) |
| `amountAfterFee` | 1 999 wei |
| rsETH minted | `1999 * 1e18 / rsETHToETHrate` |
| Fee actually paid | **0 wei** |
| Correct fee (rounded up) | 1 wei |

The depositor receives the full rsETH output as if no fee existed. Repeating this with any amount below the threshold produces the same result across all five pool contracts.

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
