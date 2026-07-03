### Title
Missing Decimal Normalization in Token-to-rsETH Swap Causes Massive Underpayment to Depositors - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `viewSwapRsETHAmountAndFee(uint256 amount, address token)` function in the pool contracts computes the rsETH/wrsETH amount to mint without normalizing the input token amount to 18 decimals. If a supported token has fewer than 18 decimals, depositors receive drastically fewer rsETH tokens than the value they deposited warrants.

### Finding Description
In `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)` — and identically in `RSETHPoolNoWrapper`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolV3ExternalBridge` — the rsETH output is computed as:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [1](#0-0) 

Both `tokenToETHRate` and `rsETHToETHrate` are in 1e18 precision. However, `amountAfterFee` is in the token's **native decimal precision**. For an 18-decimal token this is correct. For a token with `d < 18` decimals (e.g., USDC with 6), the result is `10^(18-d)` times smaller than it should be, because the formula implicitly treats the token amount as if it were already in 18-decimal units.

The `deposit(address token, uint256 amount, ...)` function then:
1. Pulls the full `amount` from the user via `safeTransferFrom` — correct, in token's native decimals.
2. Mints `rsETHAmount` to the user — wrong, computed without decimal normalization. [2](#0-1) 

This is the direct analog of the Spearbit `sponsorSeries` bug: two related operations in the same flow use inconsistent amount representations — one uses the raw token amount (the transfer), the other uses a derived amount that silently assumes 18 decimals (the mint).

The same pattern appears in: [3](#0-2) [4](#0-3) 

The `addSupportedToken` admin function has no decimal guard, so any non-18-decimal token can be added without triggering a revert.

### Impact Explanation
A depositor of a non-18-decimal token (e.g., 6-decimal USDC) would receive `10^12` times fewer wrsETH than the deposited value warrants. The excess token value is permanently locked in the pool, accruing to existing rsETH holders. This is direct, irreversible theft of depositor funds — **Critical** severity under the allowed impact scope.

### Likelihood Explanation
The `addSupportedToken` function contains no check on token decimals. Any admin legitimately extending the pool to a non-18-decimal token (USDC, USDT, or a future LST with non-standard decimals) silently activates the bug for every subsequent depositor. The current deployment uses only 18-decimal LSTs, but the code is explicitly designed to be extensible to new tokens, making this a latent Critical risk that requires no adversarial admin action — only a routine configuration step.

### Recommendation
Normalize `amountAfterFee` to 18 decimals before computing `rsETHAmount`:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
uint256 normalizedAmount = amountAfterFee * 10 ** (

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L282-292)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L301-311)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L360-370)
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
