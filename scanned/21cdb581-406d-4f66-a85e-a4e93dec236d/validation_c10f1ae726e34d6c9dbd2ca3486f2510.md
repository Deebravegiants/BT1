### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Severe Under-Minting of rsETH for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in all pool variants computes `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` without normalizing `amountAfterFee` to 18 decimals. When a supported token has fewer than 18 decimals, the result is off by a factor of `10^(18 − tokenDecimals)`, causing users to receive a negligible amount of rsETH while their full token deposit is consumed by the pool.

---

### Finding Description

The formula used across all pool variants is:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**Dimensional analysis:**

| Variable | Meaning | Precision |
|---|---|---|
| `amountAfterFee` | token amount in native wei | `10^dT` (token decimals) |
| `tokenToETHRate` | price of 1 whole token in ETH, 1e18-scaled | `10^18` |
| `rsETHToETHrate` | price of 1 rsETH in ETH, 1e18-scaled | `10^18` |

Result precision: `10^dT × 10^18 / 10^18 = 10^dT`

But rsETH has 18 decimals, so `rsETHAmount` must be in `10^18` precision. The formula is only correct when `dT = 18`. For any token with `dT < 18`, the result is under-scaled by `10^(18 − dT)`.

The ETH-only path correctly handles this by explicitly multiplying by `1e18`:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

because ETH has 18 decimals, so `amountAfterFee * 1e18` normalizes to `10^36`, and dividing by `rsETHToETHrate` (`10^18`) yields `10^18`. The token path omits this normalization step.

The same formula appears identically in:
- `RSETHPoolV3.sol` line 334
- `RSETHPoolNoWrapper.sol` line 311
- `RSETHPoolV3ExternalBridge.sol` (token path)
- `RSETHPoolV3WithNativeChainBridge.sol` line 370
- `RSETHPool.sol` line 346

---

### Impact Explanation

If a non-18-decimal token (e.g., WBTC with 8 decimals, or USDC with 6 decimals) is added as a supported token via `addSupportedToken`, any user calling `deposit(token, amount, referralId)` will:

1. Transfer their full token amount to the pool (tokens leave the user's wallet).
2. Receive `10^(18 − dT)` times fewer rsETH tokens than the correct amount.

For USDC (6 decimals): a deposit of 1,000 USDC (= `1e9` wei) at a rate of 0.0003 ETH/USDC and rsETH price of 1.05 ETH:
- **Correct rsETH**: `1e9 × 3e14 / 1.05e18 × 1e12 ≈ 2.857e17` wei rsETH (≈ 0.2857 rsETH)
- **Actual rsETH**: `1e9 × 3e14 / 1.05e18 ≈ 285,714` wei rsETH (≈ 0.000000000000285714 rsETH)
- **Loss factor**: `10^12`

The deposited tokens are bridged to L1 and are unrecoverable by the user. This constitutes direct, permanent loss of user funds.

**Impact: Critical — direct theft of user funds.**

---

### Likelihood Explanation

The vulnerability is latent: it is not triggered by the current set of supported tokens (ETH and 18-decimal LSTs). It becomes exploitable the moment any admin adds a token with fewer than 18 decimals via `addSupportedToken`. This is a legitimate, non-malicious admin action that the contract explicitly supports. No admin compromise is required — the admin may simply be unaware of the decimal normalization bug. Likelihood is **Low** given current deployments, but the code path is fully reachable by any depositor once such a token is listed.

---

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the rate ratio:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * (10 ** (18 - tokenDecimals));
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `viewSwapAssetToPremintedRsETH` (the reverse direction) and all other pool variants.

---

### Proof of Concept

1. Admin calls `addSupportedToken(USDC, usdcOracle, bridge)` on `RSETHPoolV3`.
2. `usdcOracle.getRate()` returns `3e14` (1 USDC = 0.0003 ETH, 1e18-scaled).
3. User calls `deposit(USDC, 1000e6, "ref")` — deposits 1,000 USDC.
4. `viewSwapRsETHAmountAndFee(1000e6, USDC)` executes:
   - `fee = 1000e6 * feeBps / 10_000` (assume 0 for simplicity → `amountAfterFee = 1e9`)
   - `rsETHToETHrate = 1.05e18`
   - `tokenToETHRate = 3e14`
   - `rsETHAmount = 1e9 * 3e14 / 1.05e18 = 285,714`
5. `wrsETH.mint(user, 285714)` — user receives 285,714 wei rsETH (≈ 0 rsETH).
6. 1,000 USDC is held in the pool and later bridged to L1 — permanently unrecoverable by the user.