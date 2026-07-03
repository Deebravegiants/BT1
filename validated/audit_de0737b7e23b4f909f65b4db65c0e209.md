### Title
Missing Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Massive rsETH Mis-Minting for Non-18-Decimal Tokens - (`contracts/pools/RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV3ExternalBridge.sol`)

---

### Summary

The token-deposit path of `viewSwapRsETHAmountAndFee` across all L2 pool contracts computes the rsETH output amount using raw token units without normalizing to 18 decimals. When a supported token has fewer than 18 decimals (e.g., USDC at 6), the minted rsETH is astronomically less than it should be, causing depositors to lose nearly all value. When a token has more than 18 decimals, the protocol mints far too much rsETH, causing insolvency.

---

### Finding Description

Every L2 pool contract exposes a token-deposit overload of `viewSwapRsETHAmountAndFee`:

**`RSETHPool.sol`:**
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

**`RSETHPoolV3.sol`:**
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [2](#0-1) 

**`RSETHPoolNoWrapper.sol`:**
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [3](#0-2) 

**`RSETHPoolV3ExternalBridge.sol`:**
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [4](#0-3) 

In all four cases:
- `amountAfterFee` is in the **token's native decimals** (e.g., `1e6` for 1 USDC)
- `tokenToETHRate` is in **1e18 precision** (from `IOracle.getRate()`)
- `rsETHToETHrate` is in **1e18 precision** (from `getRate()`)

The division `tokenToETHRate / rsETHToETHrate` cancels the 1e18 factors, leaving `rsETHAmount` in the **token's native decimals**, not in rsETH's 18 decimals.

Compare with the ETH path, which correctly multiplies by `1e18` to normalize:
```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [5](#0-4) 

The token path has no equivalent normalization step.

The same structural error exists in `viewSwapAssetToPremintedRsETH` (the reverse swap), which computes:
```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
``` [6](#0-5) 

Here `rsETHAmount` is in 1e18, and the result is also in 1e18, but for a 6-decimal token the actual transfer amount should be in 1e6 — so the user would receive `1e12` times more tokens than they should. [7](#0-6) 

The `addSupportedToken` function imposes no restriction on token decimals: [8](#0-7) 

---

### Impact Explanation

**Scenario A — Token with 6 decimals (e.g., USDC):**

- User deposits 1 USDC → `amountAfterFee = 1e6`
- `tokenToETHRate = 3e14` (≈ 0.0003 ETH per USDC), `rsETHToETHrate = 1.05e18`
- `rsETHAmount = 1e6 * 3e14 / 1.05e18 ≈ 285` (in raw units)
- rsETH has 18 decimals, so `285` = `2.85e-16` rsETH
- Correct amount: `1 USDC * 0.0003 ETH/USDC / 1.05 ETH/rsETH ≈ 2.86e-4 rsETH = 2.86e14` in 1e18 units
- **User receives ~1e12 times less rsETH than they should** — effectively losing all deposited value

**Scenario B — Reverse swap (`viewSwapAssetToPremintedRsETH`) with 6-decimal token:**

- Operator swaps 1 rsETH (1e18) for USDC
- `tokenAmount = 1e18 * 1.05e18 / 3e14 ≈ 3.5e21`
- This is interpreted as `3.5e21` USDC units = `3.5e15` USDC
- Correct amount: `1 rsETH * 1.05 ETH/rsETH / 0.0003 ETH/USDC ≈ 3500 USDC = 3.5e9` in 1e6 units
- **Protocol transfers `1e12` times more USDC than it should** → direct theft of pool funds

Impact classification: **Critical — direct theft of user funds (Scenario A) and protocol insolvency (Scenario B)**.

---

### Likelihood Explanation

The `addSupportedToken` function is gated to `TIMELOCK_ROLE` (or `DEFAULT_ADMIN_ROLE` in some variants), which is a normal governance operation, not a compromise. The protocol already supports multiple tokens (wstETH on Arbitrum/Optimism), and expanding to other LSTs or collateral tokens with non-18 decimals is a natural protocol evolution. No malicious intent is required — a legitimate admin adding a non-18 decimal token triggers the bug for every subsequent depositor.

---

### Recommendation

Normalize `amountAfterFee` to 1e18 before applying the rate ratio. Retrieve the token's decimals and scale accordingly:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    uint256 feeBpsForToken = tokenFeeBps[token];
    fee = amount * feeBpsForToken / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

    // Normalize amountAfterFee to 1e18
    uint8 tokenDecimals = IERC20Metadata(token).decimals();
    uint256 amountNormalized = amountAfterFee * 1e18 / 10**tokenDecimals;

    rsETHAmount = amountNormalized * tokenToETHRate / rsETHToETHrate;
}
```

Apply the inverse normalization in `viewSwapAssetToPremintedRsETH` to convert the 1e18-precision result back to the token's native decimals.

---

### Proof of Concept

Assume `RSETHPoolV3` has USDC (6 decimals) added as a supported token with a USDC/ETH oracle returning `3e14` (0.0003 ETH per USDC), and `rsETHToETHrate = 1.05e18`.

**Deposit 1000 USDC:**
```
amountAfterFee = 1000e6 = 1_000_000_000
rsETHAmount = 1_000_000_000 * 3e14 / 1.05e18
           = 3e23 / 1.05e18
           ≈ 285_714
```
`285_714` in rsETH's 18-decimal space = `2.86e-13` rsETH.

**Expected:** `1000 USDC * 0.0003 ETH/USDC / 1.05 ETH/rsETH ≈ 0.286 rsETH = 2.86e17` in 1e18 units.

**Actual minted:** `285_714` ≈ `2.86e-13` rsETH.

**Ratio:** user receives `10^12` times less rsETH than owed. The deposited 1000 USDC is effectively stolen from the user, as the pool holds the USDC but mints a negligible rsETH amount. [9](#0-8) [10](#0-9) [11](#0-10) [12](#0-11)

### Citations

**File:** contracts/pools/RSETHPool.sol (L326-347)
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

**File:** contracts/pools/RSETHPoolV3.sol (L305-307)
```text

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
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

**File:** contracts/pools/RSETHPoolV3.sol (L399-400)
```text
        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L541-554)
```text
    function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;

        emit AddSupportedToken(token);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L292-312)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-453)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L529-531)
```text

        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```
