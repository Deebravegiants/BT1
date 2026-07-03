### Title
Decimal Precision Mismatch in `viewSwapRsETHAmountAndFee` Causes Severe rsETH Underpayment for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in all RSETHPool variants computes the rsETH output using raw token units without normalizing to 18 decimals. When a supported token has fewer than 18 decimals (e.g., USDC with 6 or wBTC with 8), the formula silently produces a result that is `10^(18 - tokenDecimals)` times smaller than the correct value, causing depositors to receive a negligible amount of rsETH/wrsETH relative to the value they deposited.

### Finding Description

Every pool variant (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `RSETHPoolNoWrapper`) computes the rsETH output for a token deposit with the same formula:

```solidity
// RSETHPoolV3.sol line 334
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` is sourced from `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// ChainlinkOracleForRSETHPoolCollateral.sol line 34
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

This returns the price of **one human-readable token** (i.e., 1 USDC = 1e6 raw units) in ETH, scaled to 1e18. Similarly, `rsETHToETHrate` is the price of one rsETH in ETH, scaled to 1e18.

For the formula to be dimensionally correct, `amountAfterFee` must also represent human-readable token units (i.e., be in 18-decimal precision). For 18-decimal tokens (wstETH, rETH, etc.) this holds and the formula is correct. For a 6-decimal token like USDC:

| Variable | Value (example) |
|---|---|
| `amountAfterFee` | 1000e6 (1000 USDC in raw units) |
| `tokenToETHRate` | ~3.3e14 (price of 1 USDC in ETH × 1e18) |
| `rsETHToETHrate` | ~1.05e18 (price of 1 rsETH in ETH × 1e18) |
| **Actual result** | `1000e6 × 3.3e14 / 1.05e18 ≈ 3.14e5` rsETH units |
| **Correct result** | `1000e6 × 1e12 × 3.3e14 / 1.05e18 ≈ 3.14e17` rsETH units |

The user receives **1e12 times fewer rsETH** than they are owed. Their tokens are transferred in full, but the minted rsETH/wrsETH is essentially zero relative to the deposited value.

The `addSupportedToken` function (TIMELOCK_ROLE) does not validate token decimals, so any non-18-decimal token can be legitimately added:

```solidity
// RSETHPoolV3.sol line 541-554
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    ...
}
```

The inverse path `viewSwapAssetToPremintedRsETH` (RSETHPoolV3 line 400) has the symmetric bug — it would compute a token output 1e12 times too large, causing the transfer to always revert.

### Impact Explanation

Any user who calls `deposit(address token, uint256 amount, ...)` with a non-18-decimal supported token transfers their full token balance to the pool but receives a negligible rsETH/wrsETH amount in return. The deposited tokens remain in the pool and are not recoverable by the user. This constitutes direct theft of user funds at the protocol level.

### Likelihood Explanation

The vulnerability is latent in all pool variants and activates the moment any non-18-decimal token (e.g., USDC, wBTC) is added via `addSupportedToken`. The function is gated by `TIMELOCK_ROLE` but is a standard operational action — no compromise is required. The protocol's architecture explicitly supports arbitrary ERC-20 tokens as collateral, and the absence of a decimal check makes accidental or intentional addition of a non-18-decimal token a realistic scenario.

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the rate formula. Retrieve the token's decimals and scale accordingly:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 amountAfterFeeNormalized = amountAfterFee * (10 ** (18 - tokenDecimals));
rsETHAmount = amountAfterFeeNormalized * tokenToETHRate / rsETHToETHrate;
```

Apply the same normalization in `viewSwapAssetToPremintedRsETH` (divide the result by `10^(18 - tokenDecimals)` to convert back to native token units).

### Proof of Concept

Root cause confirmed across all pool variants:

- `RSETHPoolV3.sol` line 334: `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;` [1](#0-0) 

- `RSETHPoolV3ExternalBridge.sol` line 452: same formula [2](#0-1) 

- `RSETHPoolV3WithNativeChainBridge.sol` line 370: same formula [3](#0-2) 

- `RSETHPool.sol` line 346: same formula [4](#0-3) 

Oracle normalization (confirms `tokenToETHRate` is price of 1 human-readable token × 1e18, not 1 raw unit): [5](#0-4) 

`addSupportedToken` has no decimal guard: [6](#0-5) 

Inverse path `viewSwapAssetToPremintedRsETH` carries the symmetric bug: [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L324-335)
```text
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

**File:** contracts/pools/RSETHPoolV3.sol (L382-401)
```text
    function viewSwapAssetToPremintedRsETH(
        address token,
        uint256 rsETHAmount
    )
        public
        view
        onlySupportedTokenOrEth(token)
        returns (uint256 tokenAmount)
    {
        // Rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();

        // Rate of token in ETH
        uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
        if (tokenToETHRate == 0) revert UnsupportedOracle();

        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L541-555)
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
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L442-453)
```text
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L360-371)
```text
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

**File:** contracts/pools/RSETHPool.sol (L334-347)
```text
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```
