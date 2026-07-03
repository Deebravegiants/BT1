### Title
Token Decimal Assumption in `viewSwapRsETHAmountAndFee` Causes Massive rsETH Underpayment for Non-18-Decimal Collateral Tokens - (`contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

The L2 pool contracts compute the rsETH amount to mint for a deposited ERC20 token using a formula that implicitly assumes the deposited token has 18 decimals. When a token with fewer decimals (e.g., USDC with 6 decimals) is configured as a supported collateral, the formula produces an rsETH output that is `10^(18 - tokenDecimals)` times smaller than the correct value — a factor of `1e12` for 6-decimal tokens — causing a direct, systemic loss of user funds.

---

### Finding Description

Every L2 pool contract exposes a `viewSwapRsETHAmountAndFee(uint256 amount, address token)` overload that computes the rsETH to mint for a given ERC20 token deposit:

**`contracts/pools/RSETHPool.sol` lines 343–346:**
```solidity
// rate of token in ETH
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

// Calculate the final rsETH amount
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

The same pattern appears verbatim in:
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` lines 449–452 [2](#0-1) 
- `contracts/pools/RSETHPoolNoWrapper.sol` lines 308–311 [3](#0-2) 
- `contracts/pools/RSETHPoolV3.sol` lines 331–334 [4](#0-3) 

The oracle (`ChainlinkOracleForRSETHPoolCollateral.getRate()`) normalizes the Chainlink price to 1e18 precision, returning the price of **1 full token** (i.e., `10^tokenDecimals` base units) in ETH:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [5](#0-4) 

So `tokenToETHRate` = ETH value of 1 full token, in 1e18 precision.

The formula `amountAfterFee * tokenToETHRate / rsETHToETHrate` is only dimensionally correct when `amountAfterFee` is also in 1e18 precision (i.e., the token has 18 decimals). For a 6-decimal token:

| Variable | Value |
|---|---|
| `amountAfterFee` | `1e6` (1 USDC in base units) |
| `tokenToETHRate` | `3.33e14` (1/3000 ETH per full USDC, in 1e18) |
| `rsETHToETHrate` | `~1e18` |
| **Actual result** | `1e6 * 3.33e14 / 1e18 = 333` rsETH base units |
| **Correct result** | `3.33e14` rsETH base units (1/3000 rsETH) |
| **Error factor** | **1e12×** underpayment |

The formula implicitly requires `amountAfterFee` to be normalized to 1e18 before multiplication, but no such normalization is performed. The ETH-deposit path correctly uses `amountAfterFee * 1e18 / rsETHToETHrate` because ETH is always 18 decimals, but the token path has no equivalent normalization. [6](#0-5) 

---

### Impact Explanation

**High — Theft of user funds / contract fails to deliver promised returns.**

A user depositing 1 USDC (6 decimals) would receive `333` rsETH base units (`3.33e-16` rsETH) instead of `3.33e14` rsETH base units (`3.33e-4` rsETH). The deposited USDC is fully transferred to the pool, but the user receives `1e12×` less rsETH than owed. This is a direct, irreversible loss of user funds on every deposit of a non-18-decimal token. The pool retains the excess value, creating a permanent accounting discrepancy.

---

### Likelihood Explanation

**Medium.** The `supportedTokenOracle` mapping is admin-configurable and designed to support arbitrary ERC20 tokens beyond LSTs. USDC (6 decimals) is a natural candidate for collateral on any L2 where the protocol operates. No attacker action is required — the miscalculation fires deterministically on every deposit of any configured non-18-decimal token. The bug is silent (no revert) and affects all users equally.

---

### Recommendation

Normalize `amountAfterFee` to 1e18 precision before applying the rate formula. Query the token's decimals at configuration time (or on-the-fly) and scale accordingly:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint8 tokenDecimals = IERC20Metadata(token).decimals();
    // Normalize to 1e18 precision
    uint256 amountNormalized = amountAfterFee * 1e18 / 10 ** tokenDecimals;

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

    rsETHAmount = amountNormalized * tokenToETHRate / rsETHToETHrate;
}
```

Alternatively, cache `tokenDecimals` in the `supportedTokenOracle` mapping at the time a token is added.

---

### Proof of Concept

**Setup:** Pool on an L2 where USDC (6 decimals, price = $1, ETH = $3000) is added as a supported token. Oracle returns `tokenToETHRate = 3.33e14` (1/3000 ETH per USDC in 1e18). `rsETHToETHrate = 1e18`.

**User action:** Calls `depositAsset(USDC, 1_000_000, ...)` (1 USDC = `1e6` base units).

**Execution trace (`RSETHPool.sol` lines 335–346):**
```
fee = 1e6 * feeBps / 10_000  (small, ignore)
amountAfterFee ≈ 1e6
tokenToETHRate = 3.33e14
rsETHToETHrate = 1e18
rsETHAmount = 1e6 * 3.33e14 / 1e18 = 333
```

**Expected rsETH:** `1e6 * 1e18 / 1e6 * 3.33e14 / 1e18 = 3.33e14` (≈ 0.000333 rsETH)

**Actual rsETH minted:** `333` base units (≈ 0.000000000000333 rsETH)

**Loss:** User receives `1e12×` less rsETH than owed. The 1 USDC is permanently held by the pool with no recourse. [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPool.sol (L335-346)
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
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L449-452)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L308-311)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L305-307)
```text

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-34)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```
