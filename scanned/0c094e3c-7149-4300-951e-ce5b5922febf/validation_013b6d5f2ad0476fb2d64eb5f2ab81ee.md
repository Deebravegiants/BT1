### Title
Precision Loss in Token-to-rsETH Conversion Causes User to Receive Zero rsETH for Small Deposits - (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
In `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` and `AGETHPoolV3.viewSwapAgETHAmountAndFee`, the token-to-rsETH/agETH conversion uses bare integer division without sufficient precision. When the numerator is smaller than the denominator, the result truncates to 0. A user depositing a small amount of a supported token passes the only guard (`amount == 0`) but receives 0 rsETH while their tokens are permanently transferred to the pool.

### Finding Description
`RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee` (token overload) computes:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
// rate of rsETH in ETH
uint256 rsETHToETHrate = getRate();
// rate of token in ETH
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
// Calculate the final rsETH amount
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Both `tokenToETHRate` and `rsETHToETHrate` are 1e18-precision values. When `amountAfterFee * tokenToETHRate < rsETHToETHrate`, Solidity integer division truncates the result to 0.

The calling function `deposit(address token, uint256 amount, string memory referralId)` only checks `if (amount == 0) revert InvalidAmount()`. It then unconditionally transfers the user's tokens in and transfers `rsETHAmount` (which may be 0) out:

```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
rsETH.safeTransfer(msg.sender, rsETHAmount);   // transfers 0 rsETH
```

There is no minimum-output guard (no `minRsETHAmountExpected` parameter), so the transaction succeeds silently with the user receiving nothing.

The identical pattern exists in:
- `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee(uint256 amount)` (ETH overload): `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`
- `AGETHPoolV3.viewSwapAgETHAmountAndFee(uint256 amount, address token)`: `agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate`

### Impact Explanation
A user depositing tokens whose value in ETH is less than `rsETHToETHrate` (≈ 1e18) receives 0 rsETH. Their tokens are transferred into the pool and subsequently bridged to L1 via `moveAssetsForBridging` / `bridgeAssets`, with no recovery path for the depositor. This is a direct, permanent loss of user funds. The magnitude is bounded by the precision threshold: for a token priced at 0.5e18 ETH/token and rsETH priced at 1.1e18 ETH/rsETH, any deposit of 1–2 wei of that token yields 0 rsETH.

### Likelihood Explanation
Any unprivileged depositor can trigger this by calling `deposit(token, smallAmount, referralId)` with a non-zero but sub-threshold amount. No admin action or special condition is required. The pool contracts impose no minimum deposit beyond `amount != 0`. The practical frequency is low because normal users deposit meaningful amounts, but the path is fully reachable and requires no privilege.

### Recommendation
Use higher precision for the conversion, consistent with the `WadMath` library already present in the codebase:

```solidity
// Instead of:
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;

// Use:
rsETHAmount = amountAfterFee.mulWad(tokenToETHRate).divWad(rsETHToETHrate);
```

Alternatively, add a minimum-output parameter (analogous to `minRSETHAmountExpected` in `LRTDepositPool`) and revert if the computed output is 0.

### Proof of Concept
1. `rsETHToETHrate = 1.1e18` (rsETH has appreciated 10 %).
2. Supported token has `tokenToETHRate = 0.5e18` (worth 0.5 ETH each).
3. `feeBps = 0` for simplicity.
4. User calls `deposit(token, 2, "ref")` — depositing 2 wei of the token.
5. `fee = 2 * 0 / 10_000 = 0`; `amountAfterFee = 2`.
6. `rsETHAmount = 2 * 0.5e18 / 1.1e18 = 0` (integer truncation).
7. `IERC20(token).safeTransferFrom(user, pool, 2)` — 2 wei of token leave the user.
8. `rsETH.safeTransfer(user, 0)` — user receives nothing.
9. The 2 wei of token are pooled with other assets and eventually bridged to L1; the user has no recovery mechanism. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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

**File:** contracts/agETH/AGETHPoolV3.sol (L175-195)
```text
    function viewSwapAgETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 agETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
    }
```
