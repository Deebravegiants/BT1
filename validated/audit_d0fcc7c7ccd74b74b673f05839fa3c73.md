### Title
Precision Truncation in Token-to-rsETH Swap Causes Silent Loss of User Funds - (`contracts/pools/RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolNoWrapper.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in all L2 pool contracts computes `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` using plain integer division. When a token has small decimals (e.g., USDC at 6 decimals) and its ETH-relative rate is small, the numerator `amountAfterFee * tokenToETHRate` can truncate to zero before division, yielding `rsETHAmount = 0`. The deposit functions do not guard against a zero output, so the user's tokens are taken and they receive nothing.

---

### Finding Description

Every L2 pool contract exposes a token deposit path:

```solidity
// RSETHPool.sol (identical pattern in RSETHPoolV3, RSETHPoolNoWrapper,
// RSETHPoolV3ExternalBridge, RSETHPoolV3WithNativeChainBridge)
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    if (amount == 0) revert InvalidAmount();
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount); // tokens taken first
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    feeEarnedInToken[token] += fee;
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount); // 0 transferred silently
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The rate calculation:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount, address token)
    public view onlySupportedToken(token)
    returns (uint256 rsETHAmount, uint256 fee)
{
    uint256 feeBpsForToken = tokenFeeBps[token];
    fee = amount * feeBpsForToken / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();                                    // ~1.05e18
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // e.g. ~3.33e14 for USDC

    rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;        // truncates to 0
}
``` [2](#0-1) 

The same pattern is present verbatim in: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

**Precision arithmetic:**

- `rsETHToETHrate` ≈ `1.05e18` (rsETH/ETH, 1e18-precision)
- `tokenToETHRate` for USDC (6 decimals, $1 when ETH = $3 000) ≈ `3.33e14`
- Truncation condition: `amountAfterFee * 3.33e14 < 1.05e18` → `amountAfterFee < 3 154` USDC wei ≈ **0.003 USDC**

For any deposit below this threshold, `rsETHAmount = 0`. The ERC-20 `safeTransfer(user, 0)` succeeds silently, the user's tokens are permanently held by the pool, and no rsETH is minted. There is no zero-output guard anywhere in the deposit path.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns.**

A depositor who sends a small amount of a low-decimal token (e.g., USDC, USDT) receives 0 rsETH while their tokens are retained by the pool. The pool's `feeEarnedInToken` mapping is not incremented for the lost principal (only the fee portion is), so the funds are effectively stranded. The monetary loss per transaction is small (sub-cent for USDC), but the contract silently violates its core deposit guarantee.

---

### Likelihood Explanation

Low-to-medium. Any user who deposits a dust amount of a supported low-decimal token triggers this path. The threshold is small enough that it could be hit accidentally (e.g., a UI rounding error, a test transaction, or a griefing attempt to demonstrate the bug). The condition is deterministic and reproducible.

---

### Recommendation

1. **Add a zero-output guard** in every token deposit function:
   ```solidity
   if (rsETHAmount == 0) revert InvalidAmount();
   ```
2. **Scale intermediate values** to 1e18 precision before dividing, analogous to the ETH path which uses `amountAfterFee * 1e18 / rsETHToETHrate`. For tokens, normalize the token amount to 18 decimals before applying the rate:
   ```solidity
   uint256 normalizedAmount = amountAfterFee * 10**(18 - tokenDecimals);
   rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
   ```

---

### Proof of Concept

Assume USDC (6 decimals) is a supported token with `tokenToETHRate = 3.33e14` (USDC/ETH when ETH = $3 000) and `rsETHToETHrate = 1.05e18`.

```
amountAfterFee = 3_000  // 0.003 USDC (6 decimals)
rsETHAmount = 3_000 * 3.33e14 / 1.05e18
            = 9.99e17 / 1.05e18
            = 0  (integer truncation)
```

A user calling `deposit(USDC, 3_000, "")`:
1. `safeTransferFrom` moves 3 000 USDC wei from the user to the pool. ✓
2. `viewSwapRsETHAmountAndFee` returns `(0, 0)`.
3. `safeTransfer(user, 0)` succeeds silently.
4. User holds 0 rsETH; pool holds 3 000 USDC wei with no accounting entry.

### Citations

**File:** contracts/pools/RSETHPool.sol (L284-305)
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

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
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
