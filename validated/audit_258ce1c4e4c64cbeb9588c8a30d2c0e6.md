### Title
Wrong Decimal Normalization in Token Deposit Swap Calculation Causes Massive rsETH Underpayment - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

The `viewSwapRsETHAmountAndFee(amount, token)` function in multiple pool contracts computes the rsETH output for non-ETH token deposits without normalizing the token amount to 18-decimal precision. When a token with fewer than 18 decimals (e.g., WBTC with 8 decimals) is deposited, the user receives orders of magnitude fewer rsETH tokens than they are entitled to, effectively losing their entire deposit.

### Finding Description

The ETH deposit path correctly multiplies by `1e18` to account for ETH's 18-decimal precision:

```solidity
// ETH path — correct
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [1](#0-0) 

The token deposit path, however, omits this normalization:

```solidity
// Token path — missing decimal normalization
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [2](#0-1) 

The `tokenToETHRate` is sourced from `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which returns the price of **one whole token** in ETH, normalized to 18 decimals:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [3](#0-2) 

This means `tokenToETHRate` represents the price of 1 whole WBTC (not 1 satoshi) in ETH. But `amountAfterFee` is in native token units (satoshis for WBTC). The formula treats `amountAfterFee` as if it were already in 18-decimal precision, which it is not for sub-18-decimal tokens.

The same bug exists in all pool variants that accept non-ETH token deposits:
- `contracts/pools/RSETHPool.sol` line 346 [4](#0-3) 
- `contracts/pools/RSETHPoolNoWrapper.sol` line 311 [5](#0-4) 
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` line 452 [6](#0-5) 
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` line 370 [7](#0-6) 

### Impact Explanation

**Critical — Direct theft/permanent loss of user funds.**

For a user depositing 1 WBTC (1e8 units, price = 20 ETH, rsETH rate = 1.05 ETH):

| | Formula | Result |
|---|---|---|
| **Actual** | `1e8 * 20e18 / 1.05e18` | `≈ 1.9e9` rsETH |
| **Expected** | `(1e8 / 1e8) * 20e18 / 1.05e18` | `≈ 1.9e19` rsETH |

The user receives `1.9e9` rsETH instead of `1.9e19` rsETH — **10 orders of magnitude less**. Since the user holds essentially zero rsETH, they cannot redeem their deposited WBTC through any user-accessible path. The WBTC is permanently locked in the pool, constituting a total loss of the deposited asset.

The `dailyMintAmount` accumulator in `limitDailyMint` is also fed the same underflowed `rsETHAmount`, meaning the daily cap is effectively never reached for non-18-decimal token deposits, allowing unlimited minting of the (tiny) rsETH amount. [8](#0-7) 

### Likelihood Explanation

**High.** The pool contracts explicitly expose a `deposit(address token, uint256 amount, ...)` entry point and maintain a `supportedTokenOracle` mapping for arbitrary ERC20 tokens. The `ChainlinkOracleForRSETHPoolCollateral` contract is purpose-built to wrap any Chainlink feed for use as a token oracle. Any operator adding a sub-18-decimal token (WBTC, USDC, USDT) as a supported collateral immediately activates this bug for all depositors of that token. No special permissions are required from the depositor — any user calling `deposit(token, amount, referralId)` with a supported non-18-decimal token triggers the loss.

### Recommendation

Normalize `amountAfterFee` to 18-decimal precision before applying the rate, using the token's own `decimals()`:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 amountAfterFeeNormalized = amountAfterFee * 1e18 / (10 ** tokenDecimals);
rsETHAmount = amountAfterFeeNormalized * tokenToETHRate / rsETHToETHrate;
```

This mirrors the fix applied in the referenced Symmetrical report and makes the token path consistent with the ETH path.

### Proof of Concept

1. Admin adds WBTC (8 decimals) as a supported token in `RSETHPoolV3` with a `ChainlinkOracleForRSETHPoolCollateral` wrapping the WBTC/ETH Chainlink feed.
2. User calls `deposit(wbtc, 1e8, "ref")` — depositing 1 WBTC (worth ~20 ETH at market).
3. `viewSwapRsETHAmountAndFee(1e8, wbtc)` computes:
   - `fee = 1e8 * feeBps / 10_000` (negligible)
   - `amountAfterFee ≈ 1e8`
   - `tokenToETHRate = 20e18` (Chainlink: 1 WBTC = 20 ETH)
   - `rsETHToETHrate = 1.05e18`
   - `rsETHAmount = 1e8 * 20e18 / 1.05e18 ≈ 1.9e9`
4. User receives `1.9e9` wrsETH (worth `~1.9e9 / 1e18 ≈ 0.000000002 rsETH`).
5. User's 1 WBTC (~20 ETH) is permanently stranded in the pool; the user holds no meaningful rsETH to redeem it.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
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

**File:** contracts/pools/RSETHPool.sol (L339-347)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L304-312)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L445-453)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L363-371)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```
