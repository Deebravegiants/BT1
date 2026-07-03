### Title
Missing Decimal Normalization in `viewSwapRsETHAmountAndFee` Causes Severe rsETH Under-Minting for Non-18 Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
`RSETHPoolV3.viewSwapRsETHAmountAndFee` computes the rsETH amount to mint by multiplying the raw token amount (in the token's native decimals) directly against the oracle rate (always in 1e18 precision), without normalizing the token amount to 18 decimals first. If any supported token has fewer than 18 decimals, users receive a fraction of the rsETH they are owed, and the surplus value is permanently stranded in the pool.

### Finding Description
The token-deposit path in `RSETHPoolV3` computes the rsETH amount as:

```solidity
// contracts/pools/RSETHPoolV3.sol L324-L334
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;

uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Both `rsETHToETHrate` and `tokenToETHRate` are always expressed in 1e18 precision (confirmed by `WETHOracle`, `ChainlinkOracleForRSETHPoolCollateral`, and `InterimRSETHOracle`, all of which return or normalize to 1e18). However, `amountAfterFee` is in the token's native decimals. For an 18-decimal token the formula is dimensionally consistent; for any token with `d < 18` decimals it is off by a factor of `10^(18 - d)`.

**Concrete example — USDC (6 decimals):**

| Variable | Value |
|---|---|
| `amount` (1 USDC) | `1e6` |
| `tokenToETHRate` (≈ 1/3000 ETH, 1e18-scaled) | `≈ 3.33e14` |
| `rsETHToETHrate` | `≈ 1.05e18` |
| Computed `rsETHAmount` | `1e6 × 3.33e14 / 1.05e18 ≈ 317 wei` |
| **Correct** `rsETHAmount` | `≈ 3.17e14 wei` |

The user receives `317` wei of rsETH instead of `~3.17e14` wei — a shortfall of `10^12×`. The pool retains the full USDC deposit. Because `swapAssetToPremintedRsETH` (the only reverse-swap path) is restricted to `OPERATOR_ROLE`, the depositor has no self-service way to recover the stranded value.

The same decimal-blindness exists in the companion view function used for the reverse direction:

```solidity
// contracts/pools/RSETHPoolV3.sol L400
tokenAmount = rsETHAmount * rsETHToETHrate / tokenToETHRate;
```

This is consistent with the minting formula, so the operator-only reverse swap would return only the tiny rsETH amount's worth of tokens, not the full deposit.

The `addSupportedToken` entry point that enables this path has no decimal guard:

```solidity
// contracts/pools/RSETHPoolV3.sol L541-L554
function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    ...
}
```

### Impact Explanation
Any user who deposits a supported token with fewer than 18 decimals via `deposit(token, amount, referralId)` receives a negligible rsETH amount. The deposited tokens are held by the pool but the user holds insufficient rsETH to reclaim them through any user-accessible path. This constitutes **temporary freezing of funds** (the operator can rescue via `swapAssetToPremintedRsETH`, but the user cannot act unilaterally). Impact: **Medium — temporary freezing of funds**.

### Likelihood Explanation
`addSupportedToken` is gated by `TIMELOCK_ROLE`, so the trigger requires a governance decision to list a sub-18-decimal token (e.g., USDC, USDT, WBTC). The contract contains no technical barrier preventing such a listing, and the pool is explicitly designed to be multi-asset. Likelihood: **Low** (governance action required), but the consequence is immediate and automatic for every depositor of that token once listed.

### Recommendation
Normalize `amountAfterFee` to 18 decimals before applying the rate formula:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (18 - tokenDecimals);
rsETHAmount = normalizedAmount * tokenToETHRate / rsETHToETHrate;
```

Apply the symmetric inverse normalization in `viewSwapAssetToPremintedRsETH`. Alternatively, enforce `decimals() == 18` inside `addSupportedToken`.

### Proof of Concept
1. Deploy a mock ERC-20 with 6 decimals and a mock oracle returning `3.33e14` (≈ USDC/ETH rate in 1e18).
2. Call `addSupportedToken(mockUSDC, mockOracle)` as `TIMELOCK_ROLE`.
3. Approve and call `deposit(mockUSDC, 1e6, "")` (1 USDC).
4. Observe `wrsETH.balanceOf(msg.sender) == 317` instead of the expected `~3.17e14`.
5. Confirm the pool holds `1e6` USDC units with no user-accessible redemption path for the stranded value.

**Root cause lines:** [1](#0-0) 

**No decimal guard in token listing:** [2](#0-1) 

**Reverse-swap restricted to operator only (user cannot self-rescue):** [3](#0-2)

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

**File:** contracts/pools/RSETHPoolV3.sol (L414-450)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
        UtilLib.checkNonZeroAddress(rsETH);

        IRsETHTokenWrapper wrapper = IRsETHTokenWrapper(address(wrsETH));
        IERC20 tokenContract = IERC20(token);

        if (!wrapper.allowedTokens(rsETH)) revert TokenNotAllowedInWrapper();
        if (rsETHAmount == 0) revert InvalidAmount();
        if (rsETHAmount > wrapper.maxAmountToDepositBridgerAsset(rsETH)) revert ExceedsMaxAmountToDepositInWrapper();

        // Get the amount of token to transfer to the user for the given amount of rsETH provided
        uint256 tokenAmount = viewSwapAssetToPremintedRsETH(token, rsETHAmount);

        // Transfer rsETH from sender to the wrapper
        IERC20(rsETH).safeTransferFrom(msg.sender, address(wrapper), rsETHAmount);

        // Transfer the token from the pool to the sender
        if (token == ETH_IDENTIFIER) {
            if (getETHBalanceMinusFees() < tokenAmount) revert InsufficientETHBalanceForReverseSwap();
            (bool success,) = payable(msg.sender).call{ value: tokenAmount }("");
            if (!success) revert TransferFailed();
        } else {
            if (getTokenBalanceMinusFees(token) < tokenAmount) revert InsufficientAssetBalanceForReverseSwap();
            tokenContract.safeTransfer(msg.sender, tokenAmount);
        }

        emit ReverseSwapOccurred(msg.sender, rsETH, token, rsETHAmount, tokenAmount);
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
