### Title
Decimal Precision Mismatch in Token Deposit rsETH Calculation Causes Severe Fund Loss for Depositors - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in `RSETHPoolV3.sol` (and identically in `RSETHPool.sol`) contains a decimal precision mismatch. The formula used to compute the rsETH output for ERC-20 token deposits silently assumes the deposited token has 18 decimals. If a token with fewer decimals (e.g., USDC at 6) is added as a supported asset, depositors receive orders of magnitude less rsETH than owed, effectively losing their deposited funds with no recovery path.

---

### Finding Description

The ETH deposit path correctly normalises the input amount to 18-decimal precision before dividing by the rsETH/ETH rate:

```solidity
// RSETHPoolV3.sol – ETH path (correct)
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The explicit `* 1e18` compensates for the fact that `amountAfterFee` is already in wei (18 decimals) and `rsETHToETHrate` is also 1e18-scaled, yielding a correctly scaled rsETH amount.

The ERC-20 token path omits this normalisation:

```solidity
// RSETHPoolV3.sol – token path (incorrect)
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Here `tokenToETHRate` (returned by the oracle's `getRate()`) is always expressed in 1e18 precision (ETH per token), and `rsETHToETHrate` is also 1e18-scaled. For an 18-decimal token the formula accidentally works because `amountAfterFee` is already 1e18-scaled. For a token with `d < 18` decimals, `amountAfterFee` is only `10^d`-scaled, so the result is `10^(18-d)` times too small.

The same formula appears verbatim in `RSETHPool.sol`:

```solidity
// RSETHPool.sol – token path (identical bug)
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

The `addSupportedToken` function in both contracts accepts any ERC-20 token and its oracle without validating that the token has exactly 18 decimals:

```solidity
// RSETHPoolV3.sol
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    ...
}
```

No decimal check is performed, leaving the door open for a non-18-decimal token to be legitimately added.

---

### Impact Explanation

**Impact: Critical – direct loss of depositor funds.**

For a 6-decimal token (e.g., USDC) with `tokenToETHRate = 3e14` (≈ $0.0003 ETH/USDC) and `rsETHToETHrate = 1.05e18`:

```
Deposit: 1 000 USDC → amountAfterFee = 1_000e6

Buggy result:
  rsETHAmount = 1_000e6 * 3e14 / 1.05e18
              = 3e23 / 1.05e18
              ≈ 285_714          (≈ 2.86e-13 rsETH)

Correct result:
  normalised  = 1_000e18         (1 000 USDC in 18-decimal units)
  rsETHAmount = 1_000e18 * 3e14 / 1.05e18
              ≈ 2.86e17          (≈ 0.286 rsETH)
```

The user's 1 000 USDC is transferred into the pool, but they receive `~285 714` units of rsETH (i.e., `~2.86e-13 rsETH` in human-readable terms) instead of `~0.286 rsETH`. The deposited USDC is permanently locked in the pool with no user-accessible recovery path; the user has effectively lost their entire deposit.

The same arithmetic error affects the `viewSwapAssetToPremintedRsETH` reverse-swap path in `RSETHPoolV3.sol`, where the result would be `10^12` times too large for a 6-decimal token, draining pool reserves.

---

### Likelihood Explanation

**Likelihood: Low.**

The bug is latent: it only activates when a token with non-18 decimals is added via `addSupportedToken`, which requires `TIMELOCK_ROLE`. All currently supported tokens (ETH, wstETH, stETH, ETHx) have 18 decimals, so no user is harmed today. However, the protocol's multi-chain expansion and the absence of any decimal guard in `addSupportedToken` make it plausible that a governance proposal to add a stablecoin or other non-18-decimal asset could be passed in good faith without the proposer recognising the precision hazard. Once such a token is listed, every depositor using that token suffers an immediate, irreversible loss.

---

### Recommendation

**Short term:** Add a decimal validation guard in `addSupportedToken`:

```solidity
require(IERC20Metadata(token).decimals() == 18, "Only 18-decimal tokens supported");
```

**Long term:** Refactor `viewSwapRsETHAmountAndFee` to normalise the token amount to 18 decimals before applying the rate calculation:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Add fuzz tests covering tokens with 6, 8, and 18 decimals to catch precision regressions.

---

### Proof of Concept

1. Governance (TIMELOCK_ROLE) calls `addSupportedToken(USDC, usdcOracle)` on `RSETHPoolV3`.
2. Alice calls `deposit(USDC, 1_000e6, "ref")`.
3. Internally, `viewSwapRsETHAmountAndFee(1_000e6, USDC)` executes:
   - `fee = 0` (assuming `feeBps = 0`)
   - `amountAfterFee = 1_000e6`
   - `rsETHToETHrate = 1.05e18`
   - `tokenToETHRate = 3e14` (oracle returns 0.0003 ETH per USDC)
   - `rsETHAmount = 1_000e6 * 3e14 / 1.05e18 ≈ 285_714`
4. `wrsETH.mint(alice, 285_714)` — Alice receives `~2.86e-13 rsETH`.
5. Alice's 1 000 USDC is held by the pool; she has no mechanism to reclaim it.
6. Correct rsETH owed: `~2.86e17` (≈ 0.286 rsETH) — Alice received `~10^12` times less.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPool.sol (L637-656)
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
