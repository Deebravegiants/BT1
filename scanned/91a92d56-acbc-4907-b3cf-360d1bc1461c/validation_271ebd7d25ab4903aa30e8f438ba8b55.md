### Title
Decimal Precision Oversight in Token-to-rsETH Swap Calculation Causes Massive Under-Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol, RSETHPoolNoWrapper.sol)

---

### Summary

All L2 pool variants compute the rsETH output for token deposits using a formula that implicitly assumes the deposited token has 18 decimals. When a token with fewer decimals (e.g., USDC at 6 decimals) is added as a supported collateral, depositors receive up to `10^(18 - tokenDecimals)` times fewer rsETH/wrsETH than they are owed, while their full token balance is transferred to the pool and eventually bridged to L1.

---

### Finding Description

Every pool variant exposes a `deposit(address token, uint256 amount, ...)` function that calls `viewSwapRsETHAmountAndFee(amount, token)` to compute the rsETH output:

**`RSETHPoolV3.sol` (identical pattern in `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolNoWrapper.sol`):**

```solidity
// rate of token in ETH
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

// Calculate the final rsETH amount
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

The oracle (`ChainlinkOracleForRSETHPoolCollateral`) normalizes the Chainlink price to a fixed 1e18 scale, representing the ETH value of **1 whole token**:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
``` [2](#0-1) 

This means `tokenToETHRate` = (price of 1 whole token in ETH) × 1e18, regardless of the token's own decimal count.

The formula `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` is only dimensionally correct when `amountAfterFee` is expressed in 1e18 units (i.e., the token has 18 decimals). For a token with `d` decimals:

| Token | `amountAfterFee` for N tokens | `tokenToETHRate` | `rsETHAmount` result | Correct result |
|---|---|---|---|---|
| wstETH (18 dec) | N × 1e18 | P × 1e18 | N × P / R × 1e18 | ✓ |
| USDC (6 dec) | N × 1e6 | P × 1e18 | N × P / R × 1e6 | ✗ (off by 1e12) |

The `addSupportedToken` function accepts any ERC-20 address without enforcing 18 decimals: [3](#0-2) 

The same pattern is present in all four pool variants: [4](#0-3) [5](#0-4) 

---

### Impact Explanation

A user depositing N USDC (6 decimals) transfers `N × 1e6` raw units to the pool. The pool bridges those tokens to L1 and deposits them into `LRTDepositPool`, capturing their full ETH value. However, the user is minted only `N × P / R × 1e6` rsETH/wrsETH instead of the correct `N × P / R × 1e18` — a shortfall of exactly `10^12` for a 6-decimal token. The depositor loses virtually all of their deposited value with no recourse. This constitutes direct theft of user funds in motion.

**Impact: Critical — Direct theft of user funds.**

---

### Likelihood Explanation

The current supported tokens (wstETH, WETH) all have 18 decimals, so the bug is latent but not yet triggered. The protocol is explicitly designed to expand its supported collateral set via `addSupportedToken`. A governance action to add a widely-used 6-decimal token (USDC, USDT) — a natural protocol expansion — would immediately activate the vulnerability for every depositor of that token. No attacker action is required beyond depositing the newly-supported token; the loss is automatic and irreversible.

**Likelihood: Medium** (requires a governance-approved token addition, which is a routine protocol operation, not a compromise).

---

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the rate formula:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply this fix consistently across all four pool variants: `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, and `RSETHPoolNoWrapper.sol`. Alternatively, enforce at `addSupportedToken` time that only 18-decimal tokens may be registered.

---

### Proof of Concept

1. Governance calls `addSupportedToken(USDC, usdcOracle, usdcBridge)` on `RSETHPoolV3`.
2. Alice calls `deposit(USDC, 1_000_000e6, "ref")` (1,000,000 USDC, worth ~1,000,000 × 0.0003 ETH = 300 ETH at a hypothetical rate).
3. `viewSwapRsETHAmountAndFee` computes:
   - `amountAfterFee` = 1_000_000 × 1e6 = 1e12
   - `tokenToETHRate` = 0.0003 × 1e18 = 3e14
   - `rsETHToETHrate` ≈ 1e18 (rsETH ≈ 1 ETH)
   - `rsETHAmount` = 1e12 × 3e14 / 1e18 = **3e8** (≈ 0.0000003 rsETH)
4. Correct rsETHAmount = 1_000_000 × 1e18 × 3e14 / 1e18 = **3e20** (≈ 300 rsETH).
5. Alice receives 3e8 wrsETH instead of 3e20 — a loss of 1,000,000 USDC worth of value. Her 1,000,000 USDC is transferred to the pool and bridged to L1 in full. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
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
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L595-600)
```text
    /// @dev Adds a supported token
    /// @param token The token address
    /// @param oracle The oracle address
    /// @param bridge The bridge address
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        _addSupportedToken(token, oracle, bridge);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L449-453)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L308-312)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```
