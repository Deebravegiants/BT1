### Title
Missing Token Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Massive Under-Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

`viewSwapRsETHAmountAndFee(uint256 amount, address token)` computes the rsETH output for a deposited ERC-20 token without normalizing the token amount to 18 decimals. Because both oracle rates cancel each other out, the raw token amount (in its native decimal precision) is used directly as the rsETH output. For tokens with fewer than 18 decimals (e.g., USDC at 6 decimals), the minted wrsETH is `10^(18 - tokenDecimals)` times smaller than it should be, causing depositors to lose virtually all deposited value.

---

### Finding Description

In `RSETHPoolV3WithNativeChainBridge.sol`, the token-deposit path computes the rsETH output as:

```solidity
// rate of token in ETH
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

// Calculate the final rsETH amount
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

Both `tokenToETHRate` and `rsETHToETHrate` are 1e18-scaled values returned by oracle contracts (e.g., `ChainlinkOracleForRSETHPoolCollateral.getRate()` normalizes to 1e18). They cancel each other out in the division, leaving:

```
rsETHAmount ≈ amountAfterFee   (in token's native decimals)
```

For an 18-decimal token this is correct. For a 6-decimal token (USDC), `amountAfterFee` is in units of 1e6, so the minted rsETH is `1e12` times too small. The oracle normalization in `ChainlinkOracleForRSETHPoolCollateral` correctly scales the price to 1e18:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [2](#0-1) 

...but the pool never applies the equivalent normalization to the deposited token amount itself. The same bug is present identically in `RSETHPoolV3.sol`, `RSETHPool.sol`, `RSETHPoolV3ExternalBridge.sol`, and `AGETHPoolV3.sol`. [3](#0-2) [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**Critical — Direct theft/permanent loss of user funds.**

A user depositing 1,000 USDC (6 decimals, `amount = 1_000e6`) with ETH price ~$3,333 and rsETH/ETH rate ~1.05:

- Expected wrsETH: `1000 / 3333 / 1.05 ≈ 0.285 rsETH = 2.85e17`
- Actual wrsETH minted: `1_000e6 * 3e14 / 1.05e18 ≈ 285_714` (≈ `2.86e-13` rsETH in human terms)

The user's 1,000 USDC is transferred into the pool via `safeTransferFrom` and is permanently locked there, while the user receives a negligible dust amount of wrsETH. The deposited tokens accrue to the pool's balance and can be bridged out by the `BRIDGER_ROLE`, effectively stealing the user's funds. [6](#0-5) 

---

### Likelihood Explanation

**High.** The `deposit(address token, ...)` function is publicly callable by any user with no access restriction. The only prerequisite is that a non-18-decimal token (e.g., USDC, USDT) is added to `supportedTokenOracle`. USDC and USDT are the most common stablecoin collateral types for such pools and are explicitly the kind of token this multi-asset deposit path is designed to support. Any user who deposits such a token triggers the loss immediately and irreversibly. [7](#0-6) 

---

### Recommendation

Normalize `amountAfterFee` to 18 decimals before computing the rsETH output:

```solidity
uint256 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * (10 ** (18 - tokenDecimals));
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the same fix to `RSETHPoolV3.sol`, `RSETHPool.sol`, `RSETHPoolV3ExternalBridge.sol`, and `AGETHPoolV3.sol`.

---

### Proof of Concept

**Setup:**
- Token: USDC (6 decimals), price = $3,333/ETH → `tokenToETHRate = 3e14` (0.0003 ETH per USDC, 1e18-scaled)
- rsETH/ETH rate: `rsETHToETHrate = 1.05e18`
- User deposits 1,000 USDC → `amount = 1_000e6 = 1e9`, fee = 0 for simplicity

**Buggy calculation (current code):**
```
rsETHAmount = 1e9 * 3e14 / 1.05e18
            = 3e23 / 1.05e18
            ≈ 285_714
```
This is `285_714` wei of wrsETH — essentially zero (correct value is `~2.85e17`).

**Correct calculation:**
```
normalizedAmount = 1e9 * 1e12 = 1e21   // scale 6-decimal to 18-decimal
rsETHAmount = 1e21 * 3e14 / 1.05e18
            = 3e35 / 1.05e18
            ≈ 2.857e17                  // ≈ 0.286 rsETH ✓
```

The user loses `~0.286 rsETH` worth of value (~$953 at $3,333/ETH) on a $1,000 deposit, with the discrepancy scaling linearly with deposit size. [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L307-328)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L34-34)
```text
        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

**File:** contracts/pools/RSETHPoolV3.sol (L330-334)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L343-346)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L191-194)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
```
