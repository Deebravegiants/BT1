### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Near-Total Loss of Deposited Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
Multiple pool contracts compute the rsETH output for ERC20 token deposits using a formula that implicitly assumes the deposited token has 18 decimals. When a token with fewer decimals (e.g., 6 for USDC/USDT) is added as a supported collateral, the formula produces an rsETH amount that is `10^(18 - tokenDecimals)` times smaller than correct, causing the depositor to lose virtually all deposited value.

### Finding Description
In `RSETHPoolV3`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`, the token-deposit variant of `viewSwapRsETHAmountAndFee` computes:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`tokenToETHRate` is sourced from `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which normalises the Chainlink answer to 1e18 and represents the price of **one full human-readable token unit** in ETH (e.g., price of 1 USDC in ETH). `rsETHToETHrate` is similarly 1e18-scaled.

For an 18-decimal token the formula is dimensionally consistent:

```
rsETHAmount = (amount_in_1e18) * (ETH_per_token_in_1e18) / (ETH_per_rsETH_in_1e18)
            → result in 1e18  ✓
```

For a 6-decimal token (USDC, USDT):

```
rsETHAmount = (amount_in_1e6) * (ETH_per_token_in_1e18) / (ETH_per_rsETH_in_1e18)
            → result in 1e6  ✗  (should be 1e18)
```

The result is `1e12` times too small. A user depositing 1 000 USDC (worth ~0.4 ETH, expecting ~0.38 rsETH ≈ 3.8e17 wei) receives only ~3.8e5 wei of rsETH — effectively zero.

The correct formula must normalise for token decimals:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate * 1e18
              / (rsETHToETHrate * 10**IERC20Metadata(token).decimals());
```

### Impact Explanation
**Critical — direct theft of user funds.** The deposited tokens are transferred to the pool and subsequently bridged to L1 (benefiting the protocol), while the depositor receives a negligible rsETH credit. The shortfall is `1 - 10^(tokenDecimals - 18)` of the deposited value, which for 6-decimal tokens is 99.9999999999% of the deposit.

### Likelihood Explanation
**Low.** The bug is only triggered when a non-18-decimal token is added via `addSupportedToken`. This is an admin/timelock action. However, USDC and USDT are the most natural collateral candidates for L2 pools, and the contracts are explicitly designed to support arbitrary ERC20 tokens. No code-level guard prevents adding a 6-decimal token.

### Recommendation
Retrieve the token's `decimals()` and normalise `amountAfterFee` to 1e18 before applying the rate formula, or divide the final result by `10**(tokenDecimals - 18)` (with appropriate direction). Apply the fix uniformly across all pool variants.

### Proof of Concept
Assume:
- USDC (6 decimals) added as supported token
- `tokenToETHRate` = 4e14 (1 USDC = 0.0004 ETH, normalised to 1e18)
- `rsETHToETHrate` = 1.05e18
- User deposits 1 000 USDC → `amount = 1_000e6`, `amountAfterFee ≈ 1_000e6` (feeBps = 0 for clarity)

**Actual result:**
```
rsETHAmount = 1_000e6 * 4e14 / 1.05e18
            = 4e23 / 1.05e18
            ≈ 380_952  (≈ 3.8e5 wei rsETH)
```

**Expected result:**
```
rsETHAmount = 1_000 * 4e14 / 1.05e18 * 1e18
            ≈ 3.8e17 wei rsETH  (≈ 0.38 rsETH)
```

The user receives `3.8e5 / 3.8e17 = 1e-12` of the correct amount. The 1 000 USDC is transferred to the pool and bridged to L1 with no meaningful rsETH issued to the depositor.

**Affected lines (same root cause in all pool variants):** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The oracle normalisation that produces the 1e18-scaled rate per full token unit is confirmed here: [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L330-335)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L307-312)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L343-347)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L448-453)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L366-371)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-36)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```
