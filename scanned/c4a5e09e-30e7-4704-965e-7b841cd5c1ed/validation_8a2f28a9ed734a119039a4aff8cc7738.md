### Title
Token Deposit Yields Zero wrsETH Due to Integer Division Rounding — (`contracts/pools/RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolNoWrapper.sol`)

---

### Summary

The L2 pool `deposit(address token, uint256 amount)` functions compute the wrsETH/rsETH output via plain integer division. When the numerator `amountAfterFee * tokenToETHRate` is smaller than the denominator `rsETHToETHrate`, Solidity truncates the result to zero. No zero-output guard exists, so the user's tokens are silently absorbed by the pool while they receive nothing in return.

---

### Finding Description

Every token-deposit path in the L2 pool family calls `viewSwapRsETHAmountAndFee(amount, token)`:

```solidity
// RSETHPoolV3.sol L324-334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;

uint256 rsETHToETHrate = getRate();                          // ≈ 1.05e18
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

The result is zero whenever `amountAfterFee * tokenToETHRate < rsETHToETHrate`. The deposit function then proceeds unconditionally:

```solidity
// RSETHPoolV3.sol L284-292
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);   // mints 0 — no revert
``` [2](#0-1) 

The only input guard is `if (amount == 0) revert InvalidAmount();` — there is no guard on the *output* being zero. [3](#0-2) 

The identical pattern is present in:
- `RSETHPoolV3ExternalBridge.sol` L401–411 / L442–452
- `RSETHPoolV3WithNativeChainBridge.sol` L318–328 / L360–370
- `RSETHPoolNoWrapper.sol` L260–270 / L301–311 [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A depositor who sends a small amount of a supported ERC-20 token (particularly one with fewer than 18 decimals, or any token whose per-unit ETH value is low relative to the rsETH rate) receives zero wrsETH/rsETH. Their tokens are permanently transferred into the pool contract and become part of the bridgeable balance, with no recourse for the user. The protocol does not lose value; the user does.

Concrete threshold example (USDC, 6 decimals, `tokenToETHRate ≈ 3e14`, `rsETHToETHrate ≈ 1.05e18`):

```
rsETHAmount = 0  when  amountAfterFee * 3e14 < 1.05e18
                 ⟺  amountAfterFee < 3500   (i.e. < 0.0035 USDC)
```

Any deposit of 1–3499 USDC base units silently yields 0 wrsETH.

---

### Likelihood Explanation

**Low.** The affected deposit amounts are sub-cent for most tokens, and gas costs dwarf the value lost. However, the path is fully permissionless and requires no special conditions — any user who sends a dust amount of a supported token triggers it. It can also occur inadvertently through integrations or scripts that do not pre-simulate the output.

---

### Recommendation

Add an explicit zero-output revert in `viewSwapRsETHAmountAndFee` or at the call site in `deposit`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
```

This mirrors the short-term recommendation in the reference report ("Revert in `exitPool` if `tokenAmountOut` is zero"). Additionally, consider enforcing a per-token minimum deposit amount analogous to `minAmountToDeposit` in `LRTDepositPool`. [6](#0-5) 

---

### Proof of Concept

1. A supported token with 6 decimals (e.g., USDC) is added to `RSETHPoolV3` via `addSupportedToken`.
2. Attacker (or any user) calls `deposit(usdcAddress, 1000, "")` — depositing 0.001 USDC.
3. `viewSwapRsETHAmountAndFee(1000, usdcAddress)` computes:
   - `fee = 1000 * feeBps / 10_000` → 0 (if feeBps < 10)
   - `amountAfterFee = 1000`
   - `rsETHAmount = 1000 * 3e14 / 1.05e18 = 3e17 / 1.05e18 = 0`
4. `wrsETH.mint(msg.sender, 0)` executes — user receives nothing.
5. The 1000 USDC base units remain in the pool, credited to no one. [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L282-282)
```text
        if (amount == 0) revert InvalidAmount();
```

**File:** contracts/pools/RSETHPoolV3.sol (L284-292)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L401-411)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-270)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
```

**File:** contracts/LRTDepositPool.sol (L657-658)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
```
