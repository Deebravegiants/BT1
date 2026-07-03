### Title
Integer Division Truncation in `viewSwapRsETHAmountAndFee` Causes Depositor to Lose Tokens While Receiving Zero wrsETH - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `viewSwapRsETHAmountAndFee` functions in the L2 pool contracts compute `rsETHAmount` via integer division. When the numerator is smaller than the denominator, Solidity truncates the result to zero. No downstream check guards against a zero `rsETHAmount`, so the deposit proceeds: the user's tokens are transferred into the pool and zero wrsETH is minted or transferred back. The deposited assets are permanently locked in the pool.

---

### Finding Description

In `RSETHPoolV3.sol`, the token-deposit path computes:

```solidity
// contracts/pools/RSETHPoolV3.sol L324-334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

If `amountAfterFee * tokenToETHRate < rsETHToETHrate`, integer division yields `rsETHAmount = 0`.

The ETH-deposit path has the same structure:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

Because rsETH appreciates over time, `rsETHToETHrate` grows above `1e18`. A deposit of 1 wei ETH gives `1 * 1e18 / rsETHToETHrate = 0`.

The `deposit` functions perform no zero-check on `rsETHAmount` before minting:

```solidity
// contracts/pools/RSETHPoolV3.sol L282-292
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);   // mints 0 — no revert
``` [3](#0-2) 

The `limitDailyMint` modifier also calls `viewSwapRsETHAmountAndFee` and adds `rsETHAmount` (zero) to `dailyMintAmount`, so it does not block the transaction:

```solidity
if (dailyMintAmount + rsETHAmount > dailyMintLimit) { revert DailyMintLimitExceeded(); }
dailyMintAmount += rsETHAmount;
``` [4](#0-3) 

The same pattern is present in every pool variant that uses `viewSwapRsETHAmountAndFee`:

- `RSETHPool.sol` L346 (token path), L319 (ETH path) — transfers 0 wrsETH from pool balance
- `RSETHPoolV2.sol` L233 — mints 0 wrsETH
- `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV2NBA.sol` — same pattern confirmed by grep [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Low. Contract fails to deliver promised returns.**

A depositor who sends a dust amount (e.g., 1–2 wei of a supported LST, or 1 wei of ETH when rsETH has appreciated) receives zero wrsETH while their tokens are permanently transferred into the pool. The pool balance grows without any corresponding wrsETH liability, meaning the depositor's funds are unrecoverable. The loss per transaction is bounded by the minimum non-zero deposit that still produces `rsETHAmount = 0`, which is at most a few wei for 18-decimal tokens.

---

### Likelihood Explanation

Low. The condition requires a deposit amount small enough that `amountAfterFee * tokenToETHRate < rsETHToETHrate`. For standard 18-decimal LSTs (stETH, wstETH) with rates near `1e18`, this means deposits of 1–2 wei. Normal users are unlikely to deposit such amounts accidentally, but there is no protocol-level guard preventing it. A malicious actor could also use this to grief the pool accounting (inflating pool token balance without minting wrsETH) at negligible cost.

---

### Recommendation

Add a zero-check on `rsETHAmount` in each `deposit` function and revert if the computed output is zero:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, enforce a `minRsETHAmountExpected` parameter (as `LRTDepositPool.depositAsset` already does) so callers can specify a slippage floor. [7](#0-6) 

---

### Proof of Concept

Assume `rsETHToETHrate = 1.05e18` (rsETH has appreciated 5%) and `tokenToETHRate = 1e18` (stETH ≈ 1 ETH), `feeBps = 0`.

1. Attacker/user calls `RSETHPoolV3.deposit(stETH, 1, "")` with `amount = 1 wei`.
2. `fee = 1 * 0 / 10_000 = 0`; `amountAfterFee = 1`.
3. `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation).
4. `limitDailyMint` modifier: `dailyMintAmount + 0 <= dailyMintLimit` → passes.
5. `IERC20(stETH).safeTransferFrom(user, pool, 1)` — 1 wei stETH leaves user.
6. `wrsETH.mint(user, 0)` — user receives nothing.
7. User has lost 1 wei stETH with no recourse.

The same scenario applies to the ETH deposit path in `RSETHPoolV2.sol` and all other pool variants listed above. [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L119-123)
```text
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
```

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
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

**File:** contracts/pools/RSETHPool.sol (L340-347)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
