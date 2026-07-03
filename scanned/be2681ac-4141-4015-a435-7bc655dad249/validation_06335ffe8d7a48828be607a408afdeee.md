### Title
Missing Token Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Severe rsETH Under-Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

Multiple L2 pool contracts compute the rsETH (or agETH) amount to mint using a formula that implicitly assumes all supported tokens have 18 decimals. When a token with fewer decimals (e.g., 8 or 6) is added via `addSupportedToken`, the formula produces a result that is off by `10^(18 − tokenDecimals)`, causing depositors to receive a negligible amount of rsETH while their full token balance is transferred to the pool — a permanent loss of user funds.

---

### Finding Description

In every pool contract that accepts ERC-20 token deposits, the rsETH amount is computed as:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

`tokenToETHRate` is fetched from `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which normalises the Chainlink answer to 1e18 precision and represents the price of **one full token** (e.g., 1 USDC, 1 WBTC) in ETH:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [2](#0-1) 

For an 18-decimal token the formula is dimensionally consistent:

```
ETH_value = amountAfterFee[1e18 units] × tokenToETHRate[ETH per full token, 1e18 scaled] / 1e18
```

For a 6-decimal token (e.g., USDC) `amountAfterFee` is in 1e6 units, but `tokenToETHRate` still represents the price of 1 full USDC (= 1e6 raw units). The division by `rsETHToETHrate` (1e18-scaled) then produces a result that is `10^(18−6) = 1e12` times too small.

The same structural bug exists in:

- `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.viewSwapRsETHAmountAndFee` [4](#0-3) 
- `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` [5](#0-4) 
- `RSETHPool.viewSwapRsETHAmountAndFee` [6](#0-5) 
- `AGETHPoolV3.viewSwapAgETHAmountAndFee` [7](#0-6) 

The `addSupportedToken` function enforces only that the oracle returns a non-zero rate; it performs no check on the token's decimal count:

```solidity
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    if (IOracle(oracle).getRate() == 0) { revert UnsupportedOracle(); }
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    ...
}
``` [8](#0-7) 

The reverse-swap path `viewSwapAssetToPremintedRsETH` has the symmetric bug — it would return `10^(18−decimals)` times too many tokens for a given rsETH amount:

```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
``` [9](#0-8) 

---

### Impact Explanation

**Critical — permanent loss of user funds.**

When a non-18-decimal token is added and a user calls `deposit(token, amount, referralId)`:

1. The full `amount` of tokens is transferred from the user to the pool (`safeTransferFrom`).
2. `viewSwapRsETHAmountAndFee` returns an rsETH amount that is `10^(18 − tokenDecimals)` times smaller than the correct value.
3. The user receives a negligible rsETH balance (e.g., ~380 wei instead of ~3.81e14 wei for 1 USDC at 0.0004 ETH/USDC).
4. The deposited tokens remain in the pool with no corresponding rsETH minted — the user's funds are permanently lost.

For WBTC (8 decimals, ~30 ETH/BTC): a deposit of 1 WBTC yields ~2.86e9 wei of rsETH (~2.86e-9 rsETH) instead of ~28.57 rsETH — a loss factor of ~1e10.

---

### Likelihood Explanation

**Low.** The current supported tokens (stETH, ETHx, swETH, WETH) are all 18-decimal, so the bug is dormant today. However, the `addSupportedToken` function is permissioned only to `TIMELOCK_ROLE` and contains no decimal guard. A future governance decision to expand collateral to WBTC, USDC, or any sub-18-decimal LST would silently activate the bug. The admin need not be malicious — the code simply does not enforce the implicit 18-decimal assumption.

---

### Recommendation

Normalise `amountAfterFee` to 18 decimals before applying the oracle rate:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Alternatively, enforce `decimals() == 18` inside `addSupportedToken` and revert otherwise.

---

### Proof of Concept

**Setup**: Deploy `RSETHPoolV3` on a testnet. Add USDC (6 decimals) as a supported token with a Chainlink USDC/ETH oracle returning `4e14` (0.0004 ETH per USDC). Set `rsETHToETHrate = 1.05e18`.

**Call**: `deposit(USDC, 1_000_000 /* 1 USDC */, "ref")`

**Expected rsETH**: `(1e6 × 4e14) / 1.05e18 × 10^(18−6) = 3.81e14 wei ≈ 0.000381 rsETH`

**Actual rsETH** (current code):
```
fee = 1e6 * feeBps / 10_000  (negligible)
amountAfterFee ≈ 1e6
rsETHAmount = 1e6 * 4e14 / 1.05e18 = 4e20 / 1.05e18 ≈ 380 wei
```

The user loses 1 USDC and receives 380 wei of rsETH instead of 3.81e14 wei — a factor of ~1e12 shortfall. The 1 USDC remains locked in the pool.

### Citations

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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-36)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L301-311)
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
