The code confirms the claim. Let me verify the arithmetic precisely:

- `amountAfterFee` at line 325: in token's native decimals (e.g., `1_000e6` for USDC)
- `tokenToETHRate` at line 331: 1e18-scaled (confirmed by `ChainlinkOracleForRSETHPoolCollateral.getRate()` at line 34 which normalizes to 1e18)
- `rsETHToETHrate` at line 328: 1e18-scaled

The formula `amountAfterFee * tokenToETHRate / rsETHToETHrate` cancels the two 1e18 WAD factors, leaving the result in the token's native decimal scale — not 1e18. For 18-decimal tokens this is coincidentally correct; for any other decimal count it is wrong.

The ETH path at line 307 correctly uses `amountAfterFee * 1e18 / rsETHToETHrate` because ETH is already 18-decimal. The token path omits the equivalent normalization.

The `deposit(address token, uint256 amount, string referralId)` function at line 286 directly mints the returned (incorrect) amount, so the loss is realized on every deposit of a non-18-decimal token.

---

Audit Report

## Title
Token Decimal Mis-Accounting in `viewSwapRsETHAmountAndFee` Causes Severe wrsETH Under-Minting for Non-18-Decimal Collateral - (File: contracts/pools/RSETHPoolV3.sol)

## Summary
`viewSwapRsETHAmountAndFee(uint256 amount, address token)` multiplies the raw token-unit amount directly against a WAD-scaled oracle rate without first normalising to 18 decimals. For any supported token whose decimals differ from 18, the minted wrsETH amount is off by a factor of `10**(18 − tokenDecimals)`. Because `deposit(address, uint256, string)` mints exactly the returned amount, depositors of non-18-decimal tokens receive a tiny fraction of the wrsETH they are owed while the full token value is locked in the pool.

## Finding Description
The ETH overload correctly normalises via an explicit `1e18` factor:

```solidity
// RSETHPoolV3.sol L307
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The token overload omits this normalisation:

```solidity
// RSETHPoolV3.sol L334
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`ChainlinkOracleForRSETHPoolCollateral.getRate()` (L34) always returns a 1e18-normalised price regardless of the Chainlink feed's native decimals:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

So both `tokenToETHRate` and `rsETHToETHrate` are 1e18-scaled. The division cancels both WAD factors, leaving `rsETHAmount` in the token's native decimal scale instead of 1e18. For a 6-decimal token the result is `10**12` times smaller than correct.

The `deposit(address token, uint256 amount, string referralId)` function at L286 calls `viewSwapRsETHAmountAndFee(amount, token)` and immediately mints the returned value to the caller at L290, so the under-minting is realised on every deposit.

Exploit path:
1. Admin (TIMELOCK_ROLE) calls `addSupportedToken(USDC, oracle)` — one-time configuration step.
2. Any user calls `deposit(USDC, 1_000e6, "")`.
3. `viewSwapRsETHAmountAndFee` returns `rsETHAmount = 1_000e6 * 1e18 / 1e18 = 1_000e6` instead of `1_000e18`.
4. `wrsETH.mint(msg.sender, 1_000e6)` is executed — user receives `1e12` times fewer wrsETH than owed.
5. The 1 000 USDC remains in the pool, permanently enriching existing wrsETH holders.

No existing guard prevents this: `onlySupportedToken` only checks that the token has a registered oracle; `limitDailyMint` uses the same broken `viewSwapRsETHAmountAndFee` to compute the mint amount, so the daily limit check also operates on the deflated value and does not block the transaction.

## Impact Explanation
Direct theft of depositor funds — a Critical allowed impact. A depositor of 1 000 USDC (6 decimals, 1:1 ETH oracle, zero fee) receives `1_000e6` wrsETH (~`1e-12` wrsETH in human units) instead of `1_000e18` wrsETH (1 000 wrsETH). The full USDC value is retained by the pool. The loss is permanent and proportional to the deposit amount; every depositor of the affected token is impacted identically.

## Likelihood Explanation
The vulnerability is latent until a non-18-decimal token is added via `addSupportedToken`, which requires TIMELOCK_ROLE — one privileged configuration step. The pool is explicitly designed to accept arbitrary ERC-20 collateral (USDC, USDT, WBTC are natural candidates), making this a realistic operational step. Once any such token is live, every unprivileged depositor calling `deposit(token, amount, referralId)` triggers the loss with no further preconditions, no victim mistakes, and no race conditions. **Likelihood: Medium.**

## Recommendation
Normalise `amountAfterFee` to 18 decimals before the rate division, mirroring the ETH path:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

function viewSwapRsETHAmountAndFee(
    uint256 amount,
    address token
) public view onlySupportedToken(token) returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint8 tokenDecimals = IERC20Metadata(token).decimals();
    uint256 normalizedAmount = amountAfterFee * 1e18 / (10 ** uint256(tokenDecimals));

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

    rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
}
```

The symmetric `viewSwapAssetToPremintedRsETH` (L400) has the inverse issue and should also be corrected to scale `tokenAmount` back to the token's native decimals.

## Proof of Concept
Assumptions: USDC (6 decimals) added as supported token, `tokenToETHRate = 1e18`, `rsETHToETHrate = 1e18`, `feeBps = 0`.

**Current behaviour (L334):**
```
amountAfterFee = 1_000e6
rsETHAmount    = 1_000e6 * 1e18 / 1e18 = 1_000e6   // ≈ 1e-12 wrsETH
```

**Expected behaviour:**
```
normalizedAmount = 1_000e6 * 1e18 / 1e6 = 1_000e18
rsETHAmount      = 1_000e18 * 1e18 / 1e18 = 1_000e18  // 1 000 wrsETH
```

Foundry test plan:
1. Deploy `RSETHPoolV3` with a mock `wrsETH` and a mock rsETH oracle returning `1e18`.
2. Deploy `ChainlinkOracleForRSETHPoolCollateral` wrapping a mock Chainlink feed returning `1e8` with `decimals() = 8` (normalises to `1e18`).
3. Call `addSupportedToken(mockUSDC, oracle)` from TIMELOCK_ROLE.
4. Call `deposit(mockUSDC, 1_000e6, "")` from a user account.
5. Assert `wrsETH.balanceOf(user) == 1_000e6` (current, wrong) vs expected `1_000e18`.
6. The assertion `balanceOf == 1_000e6` will pass against the current code, confirming the bug.