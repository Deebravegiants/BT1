### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Incorrect wrsETH Minting for Non-18-Decimal Collateral Tokens - (File: contracts/pools/RSETHPoolV3.sol)

---

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in all L2 pool variants silently assumes every supported ERC-20 collateral token has 18 decimals. When a token with fewer decimals (e.g., USDC at 6 decimals) is added via `addSupportedToken`, the minting formula produces a result that is off by a factor of `10^(18 - tokenDecimals)`, causing depositors to receive a negligible amount of wrsETH and, in the reverse-swap path, allowing the pool to be drained.

---

### Finding Description

Every L2 pool variant computes the wrsETH output for a token deposit with the same formula:

```solidity
// RSETHPoolV3.sol lines 324-334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;

uint256 rsETHToETHrate = getRate();                                    // 1e18-scaled
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // 1e18-scaled

rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`ChainlinkOracleForRSETHPoolCollateral.getRate()` always normalises the Chainlink answer to 1e18:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol line 34
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

So `tokenToETHRate` and `rsETHToETHrate` are both 1e18-scaled. The formula is dimensionally correct **only when `amountAfterFee` is also 1e18-scaled**, i.e., when the token has 18 decimals.

For a 6-decimal token the raw `amount` is 1e6-scaled, so the result is `1e12` times smaller than the economically correct value.

`addSupportedToken` in every pool variant imposes no decimal constraint — it only verifies the oracle returns a non-zero rate:

```solidity
// RSETHPoolV3.sol lines 541-554
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    if (IOracle(oracle).getRate() == 0) { revert UnsupportedOracle(); }
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    ...
}
```

The same structural flaw exists in the reverse-swap path in `RSETHPoolV3.sol`:

```solidity
// RSETHPoolV3.sol lines 396-400
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

For a 6-decimal token this returns `1e12` times **more** tokens than expected, allowing the pool to be drained.

The identical pattern is present in:
- `contracts/pools/RSETHPoolNoWrapper.sol` lines 301–311
- `contracts/pools/RSETHPoolV3ExternalBridge.sol` lines 442–452
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol` lines 360–370

---

### Impact Explanation

**Deposit path (user loses funds):**
A user deposits 1 000 USDC (= `1 000e6` raw units). With `tokenToETHRate ≈ 3e14` (1 USDC ≈ 0.0003 ETH) and `rsETHToETHrate ≈ 1.05e18`:

```
rsETHAmount = 1_000e6 * 3e14 / 1.05e18 ≈ 285_714   (raw wrsETH units)
```

Expected (correct) result: `≈ 2.857e17` raw wrsETH units (≈ 0.2857 wrsETH).

The user receives `≈ 2.857e-13` wrsETH — effectively zero — while their 1 000 USDC is locked in the pool. This is **direct theft of user funds** (Critical).

**Reverse-swap path (pool drained):**
An operator calling `swapAssetToPremintedRsETH` for 1 rsETH (`1e18`) against a 6-decimal token:

```
tokenAmount = 1e18 * 1.05e18 / 3e14 ≈ 3.5e21   (raw USDC units ≈ 3.5e15 USDC)
```

Expected: ≈ 3 500 USDC. The pool is drained of its entire USDC balance in a single call.

---

### Likelihood Explanation

The `addSupportedToken` function is gated behind `TIMELOCK_ROLE`, so the vulnerability is triggered only when a non-18-decimal token is added. The protocol is deployed on Arbitrum, Unichain, Base, and other L2s where USDC (6 decimals) and USDT (6 decimals) are the dominant liquid assets. The protocol's own `RSETHPoolNoWrapper` is explicitly described as targeting chains like Arbitrum and Unichain. There is no on-chain guard preventing a 6-decimal token from being added, and the `ChainlinkOracleForRSETHPoolCollateral` wrapper already handles arbitrary Chainlink feeds, making it straightforward to configure such a token. Likelihood is **Medium**.

---

### Recommendation

Normalise `amountAfterFee` to 18 decimals before applying the rate formula, then scale the result back:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 amountNormalized = amountAfterFee * 1e18 / (10 ** tokenDecimals);
rsETHAmount = amountNormalized * tokenToETHRate / rsETHToETHrate;
```

Apply the symmetric inverse normalisation in `viewSwapAssetToPremintedRsETH`:

```solidity
uint256 tokenAmountNormalized = rsETHAmount * rsETHToETHrate / tokenToETHRate;
tokenAmount = tokenAmountNormalized * (10 ** tokenDecimals) / 1e18;
```

Apply the same fix to all affected pool variants.

---

### Proof of Concept

1. Admin calls `RSETHPoolV3.addSupportedToken(USDC, chainlinkUSDCOracle)` on an L2 where USDC has 6 decimals.
2. User approves and calls `deposit(USDC, 1_000e6, "ref")`.
3. `viewSwapRsETHAmountAndFee(1_000e6, USDC)` executes:
   - `fee = 1_000e6 * feeBps / 10_000` (small)
   - `amountAfterFee ≈ 1_000e6`
   - `tokenToETHRate = 3e14` (Chainlink USDC/ETH normalised to 1e18)
   - `rsETHToETHrate = 1.05e18`
   - `rsETHAmount = 1_000e6 * 3e14 / 1.05e18 = 285_714`
4. `wrsETH.mint(msg.sender, 285_714)` — user receives `285_714` wei of wrsETH (≈ `2.86e-13` wrsETH) instead of `≈ 2.86e17` wei (≈ 0.286 wrsETH).
5. The user's 1 000 USDC is permanently locked in the pool with no recourse. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L539-555)
```text
    /// @dev Adds a supported token
    /// @param token The token address
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L292-312)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L433-453)
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
