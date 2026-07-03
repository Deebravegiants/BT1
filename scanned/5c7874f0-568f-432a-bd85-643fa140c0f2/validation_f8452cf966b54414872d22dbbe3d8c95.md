### Title
Missing Token Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Severe rsETH Underpayment for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in `RSETHPoolV3` (and identical logic in `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `AGETHPoolV3`) multiplies a raw token amount directly by a Chainlink-normalized 18-decimal rate without first scaling the token amount to 18 decimals. When a non-18-decimal token (e.g., USDT with 6 decimals, WBTC with 8 decimals) is added as a supported collateral, depositors receive approximately `10^(18 - tokenDecimals)` times fewer rsETH/wrsETH than they are owed, while their deposited tokens are permanently retained by the pool.

### Finding Description

In `RSETHPoolV3.viewSwapRsETHAmountAndFee`:

```solidity
// contracts/pools/RSETHPoolV3.sol lines 324-334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;

uint256 rsETHToETHrate = getRate();                                    // 18-decimal
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // 18-decimal

rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`ChainlinkOracleForRSETHPoolCollateral.getRate()` normalizes the Chainlink answer to 18 decimals:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol line 34
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

This returns the price of **1 whole token** in ETH (18-decimal). However, `amountAfterFee` is in the token's **native raw units** (e.g., `1e6` for 1 USDT). The formula treats `amountAfterFee` as if it were already in 18-decimal units, producing a result that is `10^(18 - tokenDecimals)` times too small.

The correct formula requires normalizing the token amount:
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / (rsETHToETHrate * 10 ** tokenDecimals);
```

The same pattern is present in:
- `contracts/pools/RSETHPool.sol` line 346
- `contracts/pools/RSETHPoolNoWrapper.sol` line 311
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` line 452
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` line 370
- `contracts/agETH/AGETHPoolV3.sol` line 194

### Impact Explanation

**Critical — Direct theft of user funds.**

A user depositing 1 USDT (= `1e6` raw units, ETH price $3000, rsETH ≈ 1.05 ETH):

| Variable | Value |
|---|---|
| `amountAfterFee` | `1e6` |
| `tokenToETHRate` | `≈ 3.33e14` (1 USDT in ETH, 18-dec) |
| `rsETHToETHrate` | `≈ 1.05e18` |
| **Actual rsETH minted** | `1e6 * 3.33e14 / 1.05e18 ≈ 317 wei` |
| **Correct rsETH to mint** | `≈ 3.17e14 wei` (~$0.001 worth) |

The user receives **~1 trillion times fewer** rsETH than owed. Their USDT is transferred into the pool and is unrecoverable by the depositor. The pool accumulates the full token value while minting negligible rsETH.

### Likelihood Explanation

**Medium.** The pools are designed to accept arbitrary ERC-20 tokens via `addSupportedToken`. The contract imposes no restriction on token decimals. Any governance or admin action adding a non-18-decimal token (USDT, USDC, WBTC) as a supported collateral immediately activates the bug for all subsequent depositors. The `deposit(address token, uint256 amount, string referralId)` entry point is fully public and requires no special role.

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the rate calculation:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint8 tokenDecimals = IERC20Metadata(token).decimals();
    uint256 normalizedAmount = amountAfterFee * 1e18 / 10 ** uint256(tokenDecimals);

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

    rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
}
```

Apply the same fix to all affected pool contracts.

### Proof of Concept

1. Admin calls `addSupportedToken(USDT_ADDRESS, chainlinkUSDTOracle)` on `RSETHPoolV3`.
2. Attacker (or any user) calls `deposit(USDT_ADDRESS, 1_000_000, "ref")` (1 USDT = `1e6` raw units).
3. Pool pulls `1e6` USDT from the caller via `safeTransferFrom`.
4. `viewSwapRsETHAmountAndFee(1_000_000, USDT)` computes:
   - `fee = 0` (assuming 0 bps)
   - `tokenToETHRate ≈ 3.33e14` (Chainlink USDT/ETH, normalized to 18 dec)
   - `rsETHToETHrate ≈ 1.05e18`
   - `rsETHAmount = 1e6 * 3.33e14 / 1.05e18 = 317`
5. `wrsETH.mint(msg.sender, 317)` — caller receives 317 wei of wrsETH (worth ~$0 at any realistic price).
6. The 1 USDT (~$1) remains in the pool with no mechanism for the depositor to recover it.

Root cause lines: [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/agETH/AGETHPoolV3.sol (L183-195)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
    }
```
