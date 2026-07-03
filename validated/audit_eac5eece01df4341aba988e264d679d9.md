### Title
Precision Loss in Token-to-rsETH Swap Calculation for Low-Decimal Tokens — (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in the RSETHPool contracts computes the rsETH output amount without normalizing the deposited token's amount to 18 decimals. For tokens with fewer than 18 decimals (e.g., USDC with 6 decimals), the formula produces a result that is off by a factor of `10^(18 − tokenDecimals)`, causing users to receive a severely undervalued (potentially zero) amount of rsETH while their full token deposit is transferred to the pool.

---

### Finding Description

The ETH deposit path in `viewSwapRsETHAmountAndFee(uint256 amount)` correctly normalizes the ETH amount:

```solidity
// RSETHPoolV3.sol line 307
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

ETH has 18 decimals, so `amountAfterFee` is already in 1e18 units. Multiplying by `1e18` and dividing by the rate (also 1e18-precision) yields a correct 1e18-precision rsETH amount.

The token deposit path does **not** apply the same normalization:

```solidity
// RSETHPoolV3.sol line 334
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Here `amountAfterFee` is in the token's native units (e.g., `1e6` for USDC), while `tokenToETHRate` is the oracle's per-whole-token ETH price in 1e18 precision (e.g., `3e14` for USDC ≈ $0.0003 ETH). The result is:

```
rsETHAmount = (token_units) × (ETH_per_whole_token × 1e18) / (ETH_per_rsETH × 1e18)
            = token_units × rsETH_per_whole_token
```

For a 6-decimal token, `token_units` is `10^12` times smaller than the equivalent 18-decimal representation, so the result is `10^12` times smaller than the correct rsETH amount. The formula is structurally correct only for 18-decimal tokens.

The identical pattern appears in:
- `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee(uint256, address)` line 452
- `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee(uint256, address)` line 370

The `deposit(address token, uint256 amount, ...)` function performs no minimum-rsETH-output check, so a near-zero or zero `rsETHAmount` does not revert:

```solidity
// RSETHPoolV3.sol ~line 284-292
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);  // mints near-zero or 0
```

---

### Impact Explanation

**Critical — Direct theft/loss of user funds.**

A user depositing 1,000 USDC (6 decimals, `amountAfterFee = 1e9`) with `tokenToETHRate = 3e14` and `rsETHToETHrate = 1.05e18`:

- **Actual result:** `rsETHAmount = 1e9 × 3e14 / 1.05e18 ≈ 285,714` rsETH units = `~2.86e-13` rsETH (essentially zero)
- **Correct result:** `0.2857` rsETH = `~2.86e17` rsETH units

The user's 1,000 USDC is transferred to the pool, but they receive `~2.86e-13` rsETH instead of `~0.2857` rsETH — a loss of virtually their entire deposit. The pool retains the tokens with no corresponding liability.

---

### Likelihood Explanation

**Medium.** The likelihood is conditional on whether a token with fewer than 18 decimals is added to `supportedTokenOracle`. The pool's admin can add arbitrary tokens via `supportedTokenOracle[token] = oracle`. Common DeFi tokens with sub-18 decimals (USDC: 6, USDT: 6, WBTC: 8) are plausible candidates for cross-chain pool support. Once such a token is added, any unprivileged depositor calling `deposit(token, amount, referralId)` triggers the loss.

---

### Recommendation

Normalize `amountAfterFee` to 18 decimals before the calculation, analogous to the ETH path:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * (10 ** (18 - tokenDecimals));
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Alternatively, validate in `addSupportedToken` that only 18-decimal tokens are accepted, and document this restriction explicitly.

---

### Proof of Concept

**Setup:**
- Token: USDC (6 decimals)
- `feeBps = 0` (for simplicity)
- `tokenToETHRate` (oracle): `3e14` (0.0003 ETH per USDC, 1e18-precision)
- `rsETHToETHrate`: `1.05e18`
- User deposits: 1,000 USDC → `amount = 1_000_000_000` (1e9)

**Execution path:**
1. User calls `deposit(USDC, 1_000_000_000, "")` on `RSETHPoolV3`
2. `IERC20(USDC).safeTransferFrom(user, pool, 1_000_000_000)` — 1,000 USDC leaves user
3. `viewSwapRsETHAmountAndFee(1_000_000_000, USDC)` computes:
   - `fee = 0`
   - `amountAfterFee = 1_000_000_000`
   - `rsETHAmount = 1_000_000_000 * 3e14 / 1.05e18 = 3e23 / 1.05e18 ≈ 285_714`
4. `wrsETH.mint(user, 285_714)` — user receives `285_714` rsETH units = `~2.86e-13` rsETH
5. **Expected:** `~2.86e17` rsETH units (`~0.2857` rsETH)
6. **Loss:** user loses `~0.2857 rsETH` worth of value (~$1,000 at peg) while pool retains 1,000 USDC

The root cause is the missing `10^(18 − 6) = 1e12` normalization factor in the formula at: [1](#0-0) [2](#0-1) [3](#0-2) 

Compared to the correct ETH normalization at: [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L307-307)
```text
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L334-334)
```text
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L452-452)
```text
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L370-370)
```text
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
