### Title
Hardcoded 18-Decimal Assumption in Token Swap Calculation Causes Severe rsETH Under-Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
`RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)` implicitly hardcodes an 18-decimal assumption in its rsETH minting formula. If a supported token with fewer than 18 decimals is added via `addSupportedToken`, depositors receive orders of magnitude fewer rsETH tokens than they are entitled to, effectively losing their deposited funds to the pool.

### Finding Description
In `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)`:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

- `amountAfterFee` is in the token's native decimal units (e.g., `1e6` for 1 USDC with 6 decimals)
- `tokenToETHRate` is the price of **1 whole token** in ETH, normalized to 1e18 precision by `ChainlinkOracleForRSETHPoolCollateral.getRate()` via `uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals())`
- `rsETHToETHrate` is the rsETH/ETH rate in 1e18 precision

For 18-decimal tokens, `amountAfterFee = 1e18` for 1 token and the formula is dimensionally correct. For a 6-decimal token, `amountAfterFee = 1e6` for 1 token, and the formula produces a result that is `10^(18−6) = 1e12` times too small.

The correct formula must normalize `amountAfterFee` to 1e18 precision:
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate * 1e18 / (rsETHToETHrate * 10**tokenDecimals);
```

The same structural issue exists in `RSETHPool.viewSwapRsETHAmountAndFee(uint256 amount, address token)` at line 346. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
A user depositing 1 USDC (`amountAfterFee = 1_000_000`, 6 decimals) with `tokenToETHRate = 3.3e14` (≈ 0.00033 ETH/USDC) and `rsETHToETHrate = 1.05e18`:

- **Formula result:** `1_000_000 × 3.3e14 / 1.05e18 ≈ 314 wei rsETH` (≈ 3.14×10⁻¹⁶ rsETH)
- **Correct result:** `3.14e14 wei rsETH` (≈ 3.14×10⁻⁴ rsETH)

The user loses 1e12× the expected rsETH. The deposited tokens are retained by the pool while the user receives essentially zero rsETH — constituting direct theft of user funds at the protocol level. [4](#0-3) 

### Likelihood Explanation
`addSupportedToken` is callable by `TIMELOCK_ROLE` and is explicitly designed to extend the pool to arbitrary ERC20 collateral beyond ETH and 18-decimal LSTs. A future governance decision to onboard a non-18 decimal token (e.g., USDC, USDT) would silently trigger this vulnerability for every depositor of that token. The contract provides no decimal-normalization guard, so the miscalculation is invisible until funds are lost. [5](#0-4) 

### Recommendation
Use `IERC20Metadata(token).decimals()` to normalize the token amount before applying the swap formula:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
    uint8 tokenDecimals = IERC20Metadata(token).decimals();

    // Normalize amountAfterFee to 1e18 precision before dividing by rsETHToETHrate
    rsETHAmount = amountAfterFee * tokenToETHRate * 1e18
                  / (rsETHToETHrate * 10**uint256(tokenDecimals));
}
```

Apply the same fix to `RSETHPool.viewSwapRsETHAmountAndFee(uint256 amount, address token)`.

### Proof of Concept
1. Admin calls `addSupportedToken(USDC, USDC_CHAINLINK_ORACLE)` on `RSETHPoolV3`.
2. User calls `deposit(USDC, 1_000_000, "ref")` (depositing 1 USDC; 1 USDC ≈ 0.00033 ETH).
3. Internally, `viewSwapRsETHAmountAndFee(1_000_000, USDC)` executes:
   - `amountAfterFee ≈ 1_000_000`
   - `tokenToETHRate = 3.3e14` (from `ChainlinkOracleForRSETHPoolCollateral`)
   - `rsETHToETHrate = 1.05e18`
   - `rsETHAmount = 1_000_000 * 3.3e14 / 1.05e18 ≈ 314 wei`
4. `wrsETH.mint(msg.sender, 314)` — user receives 314 wei rsETH.
5. Expected rsETH: `3.14e14 wei`. Actual: `314 wei`. Loss factor: `1e12×`.
6. The pool retains the full 1 USDC while the user receives negligible rsETH. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L267-293)
```text
    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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
