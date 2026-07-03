### Title
Precision Loss in Token-to-rsETH Rate Calculation Causes Depositors to Receive Zero wrsETH - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee` function in pool contracts computes the wrsETH mint amount via integer division without guarding against a zero result. When `amountAfterFee * tokenToETHRate < rsETHToETHrate`, the division truncates to zero, and the deposit function proceeds to mint zero wrsETH while permanently transferring the user's tokens into the pool.

### Finding Description
In `RSETHPoolV3.deposit(address token, uint256 amount, string memory referralId)`, the flow is:

1. Tokens are pulled from the user via `safeTransferFrom`.
2. `viewSwapRsETHAmountAndFee(amount, token)` is called, computing:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

3. `wrsETH.mint(msg.sender, rsETHAmount)` is called with the (potentially zero) result.

There is **no check** that `rsETHAmount > 0` before minting. When `amountAfterFee * tokenToETHRate < rsETHToETHrate`, Solidity integer division truncates to zero, `mint(msg.sender, 0)` executes silently, and the user's tokens are absorbed into the pool balance with no wrsETH issued.

The same pattern is present across every pool variant:
- `contracts/pools/RSETHPoolV3.sol` [1](#0-0) 
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` [2](#0-1) 
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` [3](#0-2) 
- `contracts/agETH/AGETHPoolV3.sol` [4](#0-3) 
- `contracts/pools/RSETHPool.sol` [5](#0-4) 

The deposit entry point that transfers tokens before the zero-result mint: [6](#0-5) 

### Impact Explanation
A depositor who sends a token amount small enough that `amountAfterFee * tokenToETHRate < rsETHToETHrate` will have their tokens permanently transferred into the pool while receiving zero wrsETH. The tokens are not recoverable by the user; they become part of the pool's bridgeable balance. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value** from the allowed impact scope.

### Likelihood Explanation
For standard 18-decimal LSTs (stETH, wstETH, ETHx) with oracle rates near 1e18, the truncation to zero occurs only for sub-wei-equivalent deposits (e.g., depositing 1 wei of stETH when `rsETHToETHrate ≈ 1.05e18` yields `1 * 1e18 / 1.05e18 = 0`). The pool contracts impose no minimum deposit floor for token deposits (unlike `LRTDepositPool` which has `minAmountToDeposit`), so any user or contract that sends a dust amount hits this path silently. Likelihood is low in practice but the code path is fully reachable by any unprivileged caller.

### Recommendation
Add an explicit zero-check after computing `rsETHAmount` (or `agETHAmount`) and revert with a descriptive error if the result is zero:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, enforce a per-token minimum deposit amount analogous to `LRTDepositPool.minAmountToDeposit`.

### Proof of Concept
Assume `rsETHToETHrate = 1.05e18` (rsETH has appreciated 5%) and a supported token with `tokenToETHRate = 1e18` (e.g., stETH):

1. Attacker/user calls `RSETHPoolV3.deposit(stETH, 1, "")` (1 wei of stETH).
2. `fee = 1 * feeBps / 10_000 = 0` (rounds to zero for any `feeBps < 10_000`).
3. `amountAfterFee = 1`.
4. `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation). [7](#0-6) 
5. `IERC20(stETH).safeTransferFrom(msg.sender, address(this), 1)` — 1 wei of stETH leaves the user. [8](#0-7) 
6. `wrsETH.mint(msg.sender, 0)` — user receives nothing.
7. The 1 wei of stETH is now part of the pool's balance, bridgeable to L1, and unrecoverable by the user.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L282-292)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3.sol (L324-334)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L442-452)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L360-370)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L184-194)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L340-346)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
