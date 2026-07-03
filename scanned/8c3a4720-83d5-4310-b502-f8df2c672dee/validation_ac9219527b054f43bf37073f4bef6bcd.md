### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Incorrect rsETH Minting — (`contracts/pools/RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`)

---

### Summary

Every pool contract's token-deposit path computes the rsETH output with:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`amountAfterFee` is expressed in the deposited token's native decimals, while `tokenToETHRate` and `rsETHToETHrate` are both 18-decimal rates. For any supported token whose decimal count differs from 18, the formula produces a result that is off by `10^(18 − tokenDecimals)`, leading to catastrophic over- or under-minting of rsETH/wrsETH.

---

### Finding Description

The oracle wrapper `ChainlinkOracleForRSETHPoolCollateral.getRate()` normalises the Chainlink answer to 18 decimal precision:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18
    / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

This gives the price of **one smallest unit of the feed's base asset** expressed in 18-decimal ETH. For a wstETH/ETH feed (18-decimal token) the result is correct. For a USDC/ETH feed (6-decimal token) the result is the price of 1 USDC in ETH, still expressed in 18 decimals (≈ 3.33 × 10¹⁴).

The pool formula then does:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

where `amountAfterFee` is in the token's native decimals. For a 6-decimal token:

| Variable | Value |
|---|---|
| `amountAfterFee` (1 USDC) | 1 × 10⁶ |
| `tokenToETHRate` | ≈ 3.33 × 10¹⁴ |
| `rsETHToETHrate` | ≈ 1.05 × 10¹⁸ |
| **Computed `rsETHAmount`** | ≈ **317** |
| **Correct `rsETHAmount`** | ≈ **3.17 × 10¹⁴** |

The result is 10¹² times too small. Conversely, for a 24-decimal token the result would be 10⁶ times too large, minting enormous amounts of wrsETH for a tiny deposit.

The same structural error appears in the reverse-swap view:

```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

For a 6-decimal output token this returns a value 10¹² times too large, draining the pool.

The ETH-only deposit path is unaffected because it hard-codes `* 1e18`:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

---

### Impact Explanation

If any non-18-decimal ERC-20 is added as a supported token:

- **6-decimal token (e.g., USDC)**: every depositor receives 10¹² times fewer wrsETH than they are owed — effectively a permanent loss of deposited funds (funds frozen in the pool, unrecoverable by the user).
- **Token with > 18 decimals**: every depositor receives 10^(d−18) times more wrsETH than they are owed — protocol insolvency through unbounded minting.

Both outcomes fall within the allowed impact scope: permanent freezing of funds / protocol insolvency.

---

### Likelihood Explanation

All currently deployed supported tokens (wstETH, WETH, native ETH) are 18-decimal, so the bug is latent today. However:

- `addSupportedToken` in `RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge` is callable by `TIMELOCK_ROLE` with no decimal check.
- `RSETHPoolV3ExternalBridge` and `RSETHPoolNoWrapper` add tokens via `_addSupportedToken` called from reinitializers, also with no decimal check.
- Protocol expansion to stablecoins or non-standard LSTs is a realistic future step.
- No on-chain guard prevents a 6- or 24-decimal token from being registered.

Likelihood is **Low** (requires a governance/timelock action to add a non-18-decimal token), but the impact is **Critical** once triggered, yielding an overall **Medium** severity.

---

### Recommendation

Normalise `amountAfterFee` to 18 decimals before applying the rate formula:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the symmetric correction in `viewSwapAssetToPremintedRsETH`:

```solidity
tokenAmount = (rsETHAmount * rsETHToETHrate / tokenToETHRate)
              / 10 ** (18 - tokenDecimals);
```

Alternatively, enforce `IERC20Metadata(token).decimals() == 18` inside `addSupportedToken` / `_addSupportedToken` to prevent non-18-decimal tokens from ever being registered.

---

### Proof of Concept

**Affected formula — identical across all five pool contracts:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

**Oracle normalises to 18 decimals but does not account for token decimals in the pool formula:** [6](#0-5) 

**`addSupportedToken` has no decimal guard:** [7](#0-6) 

**Numeric walkthrough (USDC, 6 decimals):**

```
amountAfterFee  = 1_000_000          (1 USDC, 6 dec)
tokenToETHRate  = 333_000_000_000_000 (≈ 0.000333 ETH/USDC, 18 dec)
rsETHToETHrate  = 1_050_000_000_000_000_000 (1.05 ETH/rsETH, 18 dec)

computed rsETHAmount = 1e6 * 3.33e14 / 1.05e18 ≈ 317   ← 10^12 too small
correct  rsETHAmount = 1e6 * 1e12 * 3.33e14 / 1.05e18 ≈ 3.17e14
```

A depositor of 1 USDC receives effectively zero wrsETH (317 wei), losing their entire deposit. Conversely, a token with 24 decimals would cause the pool to mint 10⁶× the correct amount per deposit, draining protocol solvency.

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-452)
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
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L351-371)
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L292-311)
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
