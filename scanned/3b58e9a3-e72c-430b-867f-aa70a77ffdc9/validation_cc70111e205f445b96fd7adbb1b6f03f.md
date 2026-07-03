### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Incorrect rsETH Amount for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolNoWrapper.sol)

---

### Summary
`RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee(uint256 amount, address token)` computes the rsETH output for a deposited ERC20 token without normalizing `amount` to 18 decimals. When a supported token has fewer than 18 decimals (e.g., USDC=6, WBTC=8), the user receives a drastically underestimated rsETH amount — effectively losing their deposited tokens. When a token has more than 18 decimals, the user receives a drastically overestimated rsETH amount, draining the pool.

---

### Finding Description
In `RSETHPoolNoWrapper.sol`, the token-deposit path calls:

```solidity
// contracts/pools/RSETHPoolNoWrapper.sol L292-L312
function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();                                          // 1e18-normalized
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();     // 1e18-normalized

    rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;              // ← BUG
}
```

Both `rsETHToETHrate` and `tokenToETHRate` are 1e18-normalized (confirmed by `ChainlinkOracleForRSETHPoolCollateral.getRate()` at line 34 which explicitly scales to 1e18). The formula therefore implicitly treats `amountAfterFee` as if it were also in 18-decimal units. However, `amountAfterFee` is the raw token balance in the token's own decimal precision.

**Correct formula** (not implemented):
```
rsETHAmount = amountAfterFee * 10**(18 - tokenDecimals) * tokenToETHRate / rsETHToETHrate
```

**Concrete example — USDC (6 decimals), 1 USDC deposited:**
| Variable | Value |
|---|---|
| `amountAfterFee` | ~1e6 (1 USDC in raw units) |
| `tokenToETHRate` | ~3.33e14 (1 USDC ≈ 1/3000 ETH, 1e18-scaled) |
| `rsETHToETHrate` | ~1e18 (rsETH ≈ 1 ETH) |
| **Actual result** | `1e6 × 3.33e14 / 1e18 = 3.33e2 = 333` (≈ 0 rsETH) |
| **Correct result** | `1e6 × 1e12 × 3.33e14 / 1e18 = 3.33e14` (≈ 0.000333 rsETH) |

The user receives **1e12× less rsETH** than owed. Their 1 USDC is transferred to the pool at line 262 but the rsETH transfer at line 268 sends a negligible amount.

---

### Impact Explanation
**Critical — Direct theft of user funds.**

When a supported token with decimals < 18 is used, a depositor's full token balance is taken by the pool (`safeTransferFrom` at line 262) but the rsETH returned is scaled down by `10**(18 - decimals)`. For USDC (6 decimals) this is a 1e12× loss; for WBTC (8 decimals) it is 1e10×. The user's funds are permanently locked in the pool with no recovery path for the depositor.

For a token with decimals > 18, the inverse holds: the user receives `10**(decimals - 18)×` more rsETH than owed, draining the pool's rsETH reserve.

---

### Likelihood Explanation
**Medium.** The `addSupportedToken` function (line 573) accepts any ERC20 token address with a valid oracle. There is no check that the token has exactly 18 decimals. The protocol's design explicitly supports multiple collateral tokens on L2 chains. Common non-18-decimal tokens (USDC, USDT, WBTC) are standard collateral candidates. Any user who deposits such a token through the public `deposit(address token, uint256 amount, string referralId)` entry point (line 250) immediately triggers the loss.

---

### Recommendation
Normalize `amountAfterFee` to 18 decimals before applying the rate calculation:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Alternatively, enforce at `addSupportedToken` time that only 18-decimal tokens are accepted:
```solidity
require(IERC20Metadata(token).decimals() == 18, "Only 18-decimal tokens supported");
```

---

### Proof of Concept

1. Admin calls `addSupportedToken(USDC, usdcOracle, usdcBridge)` — USDC has 6 decimals.
2. Attacker (or any user) approves the pool for 1000 USDC (= `1000e6` raw units).
3. User calls `deposit(USDC, 1000e6, "ref")`.
4. Line 262: `IERC20(USDC).safeTransferFrom(msg.sender, address(this), 1000e6)` — 1000 USDC leaves the user.
5. Line 264: `viewSwapRsETHAmountAndFee(1000e6, USDC)` is called.
6. Line 311: `rsETHAmount = 1000e6 * 3.33e14 / 1e18 = 333000` (≈ `3.33e-13` rsETH in human units).
7. Line 268: `rsETH.safeTransfer(msg.sender, 333000)` — user receives ~0 rsETH.
8. User has lost 1000 USDC; the pool retains the USDC and the rsETH reserve is nearly untouched. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-271)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L573-592)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
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
