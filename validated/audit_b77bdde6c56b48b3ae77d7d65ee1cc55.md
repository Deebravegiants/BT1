Audit Report

## Title
Missing Token Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Massive Under-Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

## Summary
The token-deposit path in `viewSwapRsETHAmountAndFee(uint256 amount, address token)` computes rsETH output as `amountAfterFee * tokenToETHRate / rsETHToETHrate`, where both oracle rates are 1e18-scaled and cancel each other out, leaving `rsETHAmount` in the token's native decimal precision. For tokens with fewer than 18 decimals (e.g., USDC at 6 decimals), the minted wrsETH is `10^(18 - tokenDecimals)` times smaller than correct, causing depositors to permanently lose virtually all deposited value. The same bug exists identically in `RSETHPoolV3.sol`, `RSETHPool.sol`, `RSETHPoolV3ExternalBridge.sol`, and `AGETHPoolV3.sol`.

## Finding Description
In `RSETHPoolV3WithNativeChainBridge.sol`, `viewSwapRsETHAmountAndFee` computes:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`ChainlinkOracleForRSETHPoolCollateral.getRate()` normalizes the Chainlink price to 1e18 regardless of the feed's native decimals:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

Both `tokenToETHRate` and `rsETHToETHrate` are 1e18-scaled values. Their ratio is dimensionless and approximately 1 for stablecoins (e.g., USDC/ETH rate ≈ 3e14, rsETH/ETH rate ≈ 1.05e18, ratio ≈ 2.86e-4). The formula therefore reduces to:

```
rsETHAmount ≈ amountAfterFee × (tokenToETHRate / rsETHToETHrate)
```

For an 18-decimal token, `amountAfterFee` is already in 1e18 units, so the result is correct. For a 6-decimal token, `amountAfterFee` is in 1e6 units, so the result is `1e12` times too small. The ETH deposit path correctly applies `* 1e18` before dividing:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

...but the token deposit path has no equivalent normalization. The same pattern is present in all five pool contracts.

**Exploit path:**
1. Protocol admin (via TIMELOCK_ROLE) adds a non-18-decimal token (e.g., USDC) to `supportedTokenOracle` — a normal protocol operation, not an attack.
2. Any user calls `deposit(usdcAddress, 1_000e6, "")`.
3. The pool calls `safeTransferFrom` and receives 1,000 USDC.
4. `viewSwapRsETHAmountAndFee` returns `rsETHAmount ≈ 285,714` wei (≈ 2.86e-13 rsETH) instead of the correct `≈ 2.857e17` wei (≈ 0.286 rsETH).
5. `wrsETH.mint(msg.sender, 285714)` mints dust to the user.
6. The 1,000 USDC remains in the pool and is accessible to `BRIDGER_ROLE` via `moveAssetsForBridging` or `bridgeTokens`.

No existing guard prevents this: `onlySupportedToken` only checks that the oracle is set; `limitDailyMint` uses the same broken calculation; `nonReentrant` and `whenNotPaused` are irrelevant to the accounting error.

## Impact Explanation
**Critical — Direct permanent loss of user funds.** A depositor of 1,000 USDC receives ~285,714 wei of wrsETH (≈ $0 in value) while their 1,000 USDC (~$1,000) is permanently locked in the pool and extractable by the bridger. The loss scales linearly with deposit size and is irreversible. This matches the allowed impact: "Direct theft of any user funds, whether at-rest or in-motion."

## Likelihood Explanation
The `deposit(address token, uint256 amount, string)` function is publicly callable with no access restriction beyond the token being supported. USDC and USDT (6 decimals) are the most common stablecoin collateral types for multi-asset LRT pools and are the natural candidates for addition. Any user depositing such a token after it is added triggers the loss immediately and irreversibly. The only prerequisite — adding the token — is a routine protocol governance action, not an attacker capability.

## Recommendation
Normalize `amountAfterFee` to 18 decimals before computing the output in all affected pool contracts:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

uint256 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * (10 ** (18 - tokenDecimals));
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `RSETHPoolV3.sol`, `RSETHPool.sol`, `RSETHPoolV3ExternalBridge.sol`, and `AGETHPoolV3.sol`. Also audit `viewSwapAssetToPremintedRsETH` for the symmetric inverse error (over-returning tokens for non-18-decimal assets).

## Proof of Concept
**Setup (no fork required — pure arithmetic):**
- Token: USDC (6 decimals), price = $3,333/ETH → `tokenToETHRate = 3e14`
- rsETH/ETH rate: `rsETHToETHrate = 1.05e18`
- User deposits 1,000 USDC → `amount = 1_000e6 = 1e9`, fee = 0

**Current (buggy) code path** (`RSETHPoolV3WithNativeChainBridge.sol` L360–370):
```
fee = 0
amountAfterFee = 1e9
rsETHAmount = 1e9 * 3e14 / 1.05e18
            = 3e23 / 1.05e18
            ≈ 285,714   // ≈ 2.86e-13 rsETH — essentially zero
```

**Correct calculation:**
```
normalizedAmount = 1e9 * 1e12 = 1e21
rsETHAmount = 1e21 * 3e14 / 1.05e18
            = 3e35 / 1.05e18
            ≈ 2.857e17  // ≈ 0.286 rsETH ✓
```

**Foundry test plan:**
```solidity
function test_usdcDepositUnderMints() public {
    // Deploy pool with mock USDC (6 decimals), mock oracles returning
    // tokenToETHRate = 3e14, rsETHToETHrate = 1.05e18
    // Call deposit(usdc, 1_000e6, "")
    // Assert wrsETH.balanceOf(user) < 1e15  // dust
    // Assert usdc.balanceOf(pool) == 1_000e6 // full amount locked
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L335-344)
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-34)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

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

**File:** contracts/pools/RSETHPool.sol (L340-347)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L184-195)
```text
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
