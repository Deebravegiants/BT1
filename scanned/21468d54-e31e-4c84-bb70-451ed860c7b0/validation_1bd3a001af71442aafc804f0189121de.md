Now I have enough to write the finding. The vulnerability is clear from the pool contracts.

### Title
Token Decimal Normalization Missing in L2 Pool Token Swap Calculation Causes Near-Zero rsETH Minting for Non-18-Decimal Tokens - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
`RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)` and `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee(uint256 amount, address token)` compute the rsETH output using raw token amounts without normalizing to 18 decimals. For any supported token with fewer than 18 decimals (e.g., USDC=6, WBTC=8), the minted rsETH amount is understated by a factor of `10^(18 - tokenDecimals)`, causing depositors to lose their tokens while receiving a negligible rsETH balance.

### Finding Description

Both pool contracts expose a public `deposit(address token, uint256 amount, ...)` function that accepts ERC-20 tokens and mints rsETH (or wrsETH) to the caller. The rsETH amount is computed by `viewSwapRsETHAmountAndFee`:

**RSETHPoolV3** (line 334):
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**RSETHPoolNoWrapper** (line 311):
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Both `tokenToETHRate` and `rsETHToETHrate` are 1e18-precision oracle rates. `amountAfterFee` is in the token's **native precision**, not normalized to 1e18.

Compare with the ETH deposit path (RSETHPoolV3 line 307, RSETHPoolNoWrapper line 285):
```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
Here the explicit `* 1e18` correctly scales the 1e18-precision ETH amount. The token path omits this normalization step entirely.

**Concrete arithmetic for USDC (6 decimals):**

Deposit: 1,000 USDC → `amountAfterFee` = `1_000e6`
Oracle rates: `tokenToETHRate` ≈ `5e14` (1 USDC ≈ 0.0005 ETH), `rsETHToETHrate` ≈ `1.05e18`

Actual result:
```
rsETHAmount = 1_000e6 * 5e14 / 1.05e18 ≈ 476_190
```
(≈ 4.76 × 10⁻¹³ rsETH)

Correct result (with normalization):
```
rsETHAmount = 1_000e6 * 1e12 * 5e14 / 1.05e18 ≈ 4.76e17
```
(≈ 0.476 rsETH)

The user's 1,000 USDC is transferred in, but they receive `476_190` wei of rsETH — effectively zero — instead of `~4.76e17` wei. The error factor is `10^12` for USDC and `10^10` for WBTC.

### Impact Explanation

**Critical — Direct theft of user funds.**

Any user calling `deposit(token, amount, referralId)` on `RSETHPoolV3` or `RSETHPoolNoWrapper` with a supported token that has fewer than 18 decimals loses their entire deposit. The tokens are transferred from the user to the pool contract, but the rsETH minted is so small (sub-wei equivalent in real value) that it is economically indistinguishable from zero. The deposited tokens accumulate in the pool and are subsequently bridged to L1, permanently lost to the depositor.

### Likelihood Explanation

**High.** The `deposit(address token, uint256 amount, string referralId)` function is publicly callable with no access restriction. Any user who deposits a non-18-decimal token (USDC, WBTC, etc.) through the L2 pool triggers the bug automatically. The protocol explicitly supports non-ETH token deposits via `addSupportedToken`, and USDC/WBTC are common LST-adjacent assets on L2s. No special conditions, front-running, or attacker coordination is required — the loss occurs on every such deposit.

### Recommendation

Normalize `amountAfterFee` to 18 decimals before applying the oracle rate ratio. Retrieve the token's decimals and scale accordingly:

```solidity
uint8 tokenDecimals = IERC20Metadata(token).decimals();
rsETHAmount = amountAfterFee * (10 ** (18 - tokenDecimals)) * tokenToETHRate / rsETHToETHrate;
```

Or equivalently, use a `mulDiv` pattern:
```solidity
rsETHAmount = amountAfterFee.mulDiv(tokenToETHRate * 1e18 / (10 ** tokenDecimals), rsETHToETHrate);
```

Apply the same fix to `viewSwapAssetToPremintedRsETH` in `RSETHPoolV3` (line 400), which has the symmetric error in the reverse direction.

### Proof of Concept

1. Admin calls `addSupportedToken(USDC, usdcOracle, ...)` on `RSETHPoolV3` or `RSETHPoolNoWrapper`.
2. User calls `deposit(USDC, 1_000e6, "ref")`.
3. Contract executes `viewSwapRsETHAmountAndFee(1_000e6, USDC)`:
   - `fee = 1_000e6 * feeBps / 10_000` (small)
   - `amountAfterFee ≈ 1_000e6`
   - `tokenToETHRate = usdcOracle.getRate()` → `5e14`
   - `rsETHToETHrate = rsETHOracle.getRate()` → `1.05e18`
   - `rsETHAmount = 1_000e6 * 5e14 / 1.05e18 = 476_190`
4. `wrsETH.mint(msg.sender, 476_190)` — user receives `476_190` wei of rsETH (≈ $0.000000000001).
5. `IERC20(USDC).safeTransferFrom(msg.sender, address(this), 1_000e6)` — user's 1,000 USDC is taken.
6. User has lost ~$1,000 of USDC for a negligible rsETH balance.

**Affected lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L271-292)
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-270)
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
