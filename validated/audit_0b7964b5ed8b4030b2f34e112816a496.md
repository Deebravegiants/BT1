### Title
Token Decimal Mismatch in `viewSwapRsETHAmountAndFee` Causes Depositors of Non-18 Decimal Tokens to Receive Near-Zero rsETH - (File: contracts/pools/RSETHPool.sol, RSETHPoolV3.sol, RSETHPoolNoWrapper.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

Every pool contract's `viewSwapRsETHAmountAndFee(uint256 amount, address token)` overload computes the rsETH output as:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Both `tokenToETHRate` and `rsETHToETHrate` are oracle values normalised to 1e18. The formula is therefore only correct when `amountAfterFee` is also expressed in 1e18 units, i.e. when the deposited token has 18 decimals. For any token with fewer decimals (e.g. USDC at 6), the numerator is 10^(18−d) times too small and the user receives a proportionally tiny rsETH amount while surrendering the full token balance to the pool.

---

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` always normalises its Chainlink answer to 1e18:

```solidity
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

So `tokenToETHRate` and `rsETHToETHrate` are both 1e18-scaled. The swap formula then reduces to:

```
rsETHAmount ≈ amountAfterFee × (tokenToETHRate / rsETHToETHrate)
```

where the ratio is dimensionless and close to 1 for LSTs. For an 18-decimal token this is correct. For a 6-decimal token the `amountAfterFee` is 10^12 times smaller than the equivalent 18-decimal representation, so the output is 10^12 times too small.

The same structural formula appears identically in five pool contracts:

- `RSETHPool.sol` line 346
- `RSETHPoolV3.sol` line 334
- `RSETHPoolNoWrapper.sol` line 311
- `RSETHPoolV3ExternalBridge.sol` (same pattern)
- `RSETHPoolV3WithNativeChainBridge.sol` (same pattern)

`addSupportedToken` / `_addSupportedToken` performs no decimal check; it only verifies the oracle returns a non-zero rate.

Additionally, `RSETHPoolV3ExternalBridge.sol` and `RSETHPoolV3WithNativeChainBridge.sol` expose a reverse-swap path (`viewSwapAssetToPremintedRsETH`, confirmed by the `ReverseSwapOccurred` event and `InsufficientAssetBalanceForReverseSwap` error) that uses the inverse formula:

```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

For a 6-decimal token this would return 10^12 times *more* tokens than owed, potentially draining the pool. The state-changing counterpart was not fully read within available iterations; its exploitability is flagged as uncertain but strongly implied.

---

### Impact Explanation

A user who calls `deposit(token, amount, referralId)` with a non-18 decimal token (e.g. 1 000 USDC = 1 000e6):

- `amountAfterFee` = ~1 000e6
- `tokenToETHRate` = ~3e14 (0.0003 ETH/USDC, 1e18-normalised)
- `rsETHToETHrate` = ~1.05e18

`rsETHAmount = 1 000e6 × 3e14 / 1.05e18 ≈ 285 714` (wei of rsETH, i.e. ~2.86 × 10⁻¹³ rsETH)

Expected: ~0.286 rsETH = 2.86 × 10¹⁷ wei. The user receives 10¹² times less rsETH than owed while the full USDC balance is transferred to the pool and eventually bridged to L1 — permanently unrecoverable by the depositor.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The bug is latent until a non-18 decimal token is added via `addSupportedToken` (gated by `TIMELOCK_ROLE`). This is a normal governance action, not a compromise. The protocol already supports adding arbitrary ERC-20 collateral tokens; USDC and USDT are natural candidates on any L2. No attacker action is required — any good-faith depositor of such a token is affected.

---

### Recommendation

Normalise `amountAfterFee` to 18 decimals before applying the rate ratio:

```solidity
import { IERC20Metadata } from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

uint8 tokenDecimals = IERC20Metadata(token).decimals();
rsETHAmount = amountAfterFee * 10 ** (18 - tokenDecimals) * tokenToETHRate / rsETHToETHrate;
```

Apply the symmetric correction to the reverse-swap formula:

```solidity
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate / 10 ** (18 - tokenDecimals);
```

Apply the fix consistently across all five pool contracts. Also add a decimal check (e.g. `require(decimals <= 18)`) inside `addSupportedToken` / `_addSupportedToken` as a defence-in-depth guard.

---

### Proof of Concept

**Forward swap — user loses funds:**

1. Admin adds USDC (6 decimals) as a supported token with a Chainlink oracle returning `3e14` (0.0003 ETH/USDC normalised to 1e18).
2. User calls `RSETHPool.deposit(USDC, 1_000e6, "")`.
3. `viewSwapRsETHAmountAndFee(1_000e6, USDC)` executes:
   - `fee = 0` (feeBps = 0 for simplicity)
   - `rsETHToETHrate = 1.05e18`
   - `tokenToETHRate = 3e14`
   - `rsETHAmount = 1_000e6 * 3e14 / 1.05e18 = 285_714`
4. User receives 285 714 wei of rsETH ≈ 2.86 × 10⁻¹³ rsETH.
5. Expected: `1_000e6 * 3e14 * 1e12 / 1.05e18 ≈ 2.857e17` wei = 0.286 rsETH.
6. The 1 000 USDC is held by the pool and bridged to L1; the user cannot recover it. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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
