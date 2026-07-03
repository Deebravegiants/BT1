### Title
Missing Token Decimal Normalization in L2 Pool Token Deposit Calculation - (`contracts/pools/RSETHPoolV3.sol`)

---

### Summary
The `viewSwapRsETHAmountAndFee(amount, token)` function in all L2 pool variants (`RSETHPoolV3`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) computes the wrsETH/rsETH amount to mint by multiplying the raw token amount directly by a 1e18-normalized oracle rate, without first normalizing the token amount to 1e18. When any non-18-decimal token (e.g., USDC with 6 decimals, WBTC with 8 decimals) is added as a supported token, depositors receive a negligible amount of wrsETH relative to the value they deposit, effectively losing their funds to the pool.

---

### Finding Description

Every L2 pool variant exposes a `deposit(address token, uint256 amount, ...)` path that calls `viewSwapRsETHAmountAndFee(amount, token)`. The core calculation is:

```solidity
// RSETHPoolV3.sol lines 331-334
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
// Calculate the final rsETH amount
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

The oracle (`ChainlinkOracleForRSETHPoolCollateral`) normalizes its output to 1e18 precision:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [2](#0-1) 

So `tokenToETHRate` and `rsETHToETHrate` are both 1e18-scaled. The formula therefore implicitly assumes `amountAfterFee` is also in 1e18 precision. For 18-decimal tokens this holds, but for tokens with fewer decimals the raw `amount` is orders of magnitude smaller than 1e18, producing a proportionally tiny `rsETHAmount`.

The same pattern is present in all pool variants:

- `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` line 311 [3](#0-2) 
- `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee` line 452 [4](#0-3) 
- `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee` line 370 [5](#0-4) 

Tokens are added via `addSupportedToken(address token, address oracle)`, which requires only `TIMELOCK_ROLE` and performs no decimal check:

```solidity
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    if (IOracle(oracle).getRate() == 0) revert UnsupportedOracle();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
``` [6](#0-5) 

---

### Impact Explanation

**Critical — direct theft of depositor funds.**

When a non-18-decimal token is added as a supported token, a depositor transfers their full token balance to the pool contract but receives a negligible wrsETH amount in return. The deposited tokens are then bridged to L1 and absorbed into the protocol's TVL, benefiting all existing rsETH holders at the expense of the depositor.

**Numerical example — USDC (6 decimals), 1 USDC deposit:**

| Variable | Value |
|---|---|
| `amountAfterFee` | `1e6` (1 USDC raw) |
| `tokenToETHRate` | `~3.33e14` (1/3000 ETH, 1e18-normalized) |
| `rsETHToETHrate` | `~1e18` |
| **Actual `rsETHAmount`** | `1e6 × 3.33e14 / 1e18 = 333` wrsETH units |
| **Correct `rsETHAmount`** | `1e6 × 1e12 × 3.33e14 / 1e18 = 3.33e14` wrsETH units |

The depositor receives `1e12×` fewer wrsETH than owed — effectively zero — while the pool retains the full USDC value.

---

### Likelihood Explanation

**Medium.** The vulnerability is latent until a non-18-decimal token is added via `addSupportedToken`. This is a routine protocol expansion operation (not a compromise), and the protocol's generic token support mechanism is explicitly designed to accommodate arbitrary ERC-20 tokens. Tokens like USDC (6 decimals) or WBTC (8 decimals) are natural candidates for future support on L2 chains. No attacker action is required; the bug activates automatically upon a legitimate governance action.

---

### Recommendation

Normalize `amountAfterFee` to 1e18 before applying the rate ratio:

```diff
function viewSwapRsETHAmountAndFee(
    uint256 amount,
    address token
) public view onlySupportedToken(token) returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

+   uint8 tokenDecimals = IERC20Metadata(token).decimals();
+   uint256 normalizedAmount = amountAfterFee * 1e18 / (10 ** tokenDecimals);
-   rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
+   rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
}
```

Apply the same fix to all pool variants.

---

### Proof of Concept

1. Admin calls `RSETHPoolV3.addSupportedToken(USDC, usdcOracle)` — a normal governance operation.
2. Attacker (or any user) calls `deposit(USDC, 3000e6, "")` — depositing 3000 USDC (~1 ETH in value).
3. Contract executes:
   - `tokenToETHRate = usdcOracle.getRate()` → `~3.33e14` (1/3000 ETH, 1e18-normalized)
   - `rsETHToETHrate = getRate()` → `~1e18`
   - `rsETHAmount = 3000e6 * 3.33e14 / 1e18 = ~1e6` wrsETH units (= `1e-12` wrsETH)
4. User receives `~1e-12` wrsETH (worth essentially nothing) while 3000 USDC is transferred to the pool and eventually bridged to L1.
5. The L1 TVL increases by ~1 ETH worth of USDC, inflating rsETH price for all existing holders — the depositor's value is redistributed to the protocol.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L330-334)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-34)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L308-311)
```text
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L367-370)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
