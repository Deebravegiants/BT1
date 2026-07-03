### Title
ERC20 Token Decimal Assumption in Pool Swap Calculations Causes Incorrect rsETH Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) calculate rsETH mint amounts for ERC20 token deposits using a formula that implicitly assumes all supported tokens have 18 decimals. No decimal normalization is applied, and `addSupportedToken` imposes no decimal restriction. If a non-18 decimal token (e.g., USDC with 6 decimals) is added as a supported token, depositors would receive a drastically wrong rsETH amount — effectively losing their deposited funds.

### Finding Description
In `viewSwapRsETHAmountAndFee(uint256 amount, address token)`, the rsETH mint amount is computed as:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`amountAfterFee` is the raw token amount in the token's native units (e.g., `1e6` for 1 USDC). `tokenToETHRate` is the oracle rate expressed in 1e18 precision (e.g., `3e14` for 1 USDC = 0.0003 ETH). `rsETHToETHrate` is also in 1e18 precision.

For a 18-decimal token like WETH, this works correctly:
- `1e18 * 1e18 / 1.05e18 ≈ 9.52e17` (≈ 0.952 rsETH) ✓

For a 6-decimal token like USDC (1000 USDC = `1e9` units, `tokenToETHRate = 3e14`):
- `1e9 * 3e14 / 1.05e18 ≈ 285714` (≈ 2.86e-13 rsETH) ✗

The correct result should be `≈ 2.857e17` (≈ 0.286 rsETH). The formula underestimates by a factor of `10^(18-6) = 1e12`.

The same mis-accounting affects the reverse direction in `viewSwapAssetToPremintedRsETH`:
```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```
For a 6-decimal token, this would compute a `tokenAmount` that is `1e12` times too large, causing the transfer to revert due to insufficient pool balance.

`addSupportedToken` performs no decimal check:

```solidity
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    // ...
    if (IOracle(oracle).getRate() == 0) {
        revert UnsupportedOracle();
    }
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
}
```

### Impact Explanation
If a non-18 decimal ERC20 token is added as a supported pool asset, any user calling `deposit(address token, uint256 amount, string referralId)` would have their tokens transferred into the pool but receive `10^(18 - decimals)` times fewer rsETH than the correct amount. For USDC (6 decimals), this is a factor of `1e12` — effectively zero rsETH. The deposited tokens remain locked in the pool with no mechanism for the user to recover them proportionally. This constitutes direct loss of user funds.

**Impact: Critical — Direct theft/permanent loss of user funds for depositors of non-18 decimal tokens.**

### Likelihood Explanation
The `addSupportedToken` function is callable by the `TIMELOCK_ROLE`, a legitimate governance action. The protocol already supports multiple LSTs (all 18-decimal), and there is no documented restriction against adding non-18 decimal tokens. A governance proposal to add a stablecoin (USDC, USDT) as a pool asset — a common DeFi pattern — would silently activate this bug. No attacker action is required beyond a normal user deposit after such a token is listed.

**Likelihood: Medium** — requires a governance listing of a non-18 decimal token, which is a plausible future action given the pool's multi-token architecture.

### Recommendation
1. Add a decimal check in `addSupportedToken` to enforce 18-decimal tokens only:
   ```solidity
   require(IERC20Metadata(token).decimals() == 18, "Token must have 18 decimals");
   ```
2. Alternatively, normalize `amountAfterFee` to 18 decimals before applying the formula:
   ```solidity
   uint8 tokenDecimals = IERC20Metadata(token).decimals();
   uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
   rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
   ```
   Apply the same normalization in `viewSwapAssetToPremintedRsETH` (inverse direction).

### Proof of Concept

**Affected formula in `RSETHPoolV3.viewSwapRsETHAmountAndFee`:** [1](#0-0) 

**Same pattern in `RSETHPoolV3ExternalBridge`:** [2](#0-1) 

**Same pattern in `RSETHPoolV3WithNativeChainBridge`:** [3](#0-2) 

**Reverse swap also affected:** [4](#0-3) 

**`addSupportedToken` has no decimal check:** [5](#0-4) 

**Concrete scenario:**
1. Governance calls `addSupportedToken(USDC_ADDRESS, USDC_ORACLE)` — no decimal check blocks this.
2. User calls `deposit(USDC_ADDRESS, 1000e6, "ref")` — 1000 USDC transferred to pool.
3. `viewSwapRsETHAmountAndFee(1000e6, USDC)` computes: `1000e6 * 3e14 / 1.05e18 ≈ 285714` (≈ 0 rsETH in practical terms).
4. User receives ~0 rsETH while 1000 USDC is locked in the pool — direct loss of $1000.

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

**File:** contracts/pools/RSETHPoolV3.sol (L396-401)
```text
        uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
        if (tokenToETHRate == 0) revert UnsupportedOracle();

        // Calculate the amount of token user will get for the amount of rsETH
        tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
    }
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
