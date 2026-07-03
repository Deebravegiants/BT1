### Title
Missing Minimum Output Validation Allows Zero rsETH Returned for Dust Token Deposits - (File: contracts/pools/RSETHPool.sol)

### Summary

Every L2 pool contract (`RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) accepts ERC-20 token deposits and computes the rsETH output via integer division. When the deposited amount is small enough that the division truncates to zero, the contract silently accepts the user's tokens and transfers/mints 0 rsETH in return. There is no minimum-output guard anywhere in the deposit path.

### Finding Description

The token-deposit path in every pool variant follows the same pattern:

```solidity
// e.g. RSETHPool.sol lines 284-305
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    if (amount == 0) revert InvalidAmount();

    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);   // ← tokens taken

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

    feeEarnedInToken[token] += fee;

    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);        // ← 0 rsETH sent
}
```

The output is computed as:

```solidity
// RSETHPool.sol lines 326-347
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Solidity integer division truncates toward zero. Whenever `amountAfterFee * tokenToETHRate < rsETHToETHrate`, `rsETHAmount` evaluates to `0`. The deposit function does **not** revert on a zero output; it proceeds to call `safeTransfer(msg.sender, 0)` (or `mint(msg.sender, 0)`), which succeeds silently. The user's tokens are permanently held by the pool with no rsETH issued.

The same pattern is present in all five pool variants:

- `RSETHPool.deposit(address,uint256,string)` [1](#0-0) 
- `RSETHPoolNoWrapper.deposit(address,uint256,string)` [2](#0-1) 
- `RSETHPoolV3.deposit(address,uint256,string)` [3](#0-2) 
- `RSETHPoolV3ExternalBridge.deposit(address,uint256,string)` [4](#0-3) 
- `RSETHPoolV3WithNativeChainBridge.deposit(address,uint256,string)` [5](#0-4) 

The shared calculation that produces the zero output: [6](#0-5) 

### Impact Explanation

A user who deposits a dust amount of a supported ERC-20 token (e.g., 1 wei of wstETH) will have their tokens transferred into the pool and receive 0 rsETH in return. The tokens are not refunded; they accumulate in the pool's balance and are eventually bridged to L1 as protocol revenue. The user suffers a complete loss of the deposited dust amount.

The maximum amount losable in a single call is bounded by `⌈rsETHToETHrate / tokenToETHRate⌉ − 1` wei of the deposited token. For ETH-pegged LSTs (stETH, wstETH, ETHx) where `tokenToETHRate ≈ rsETHToETHrate ≈ 1e18`, this ceiling is approximately 1 wei per call — negligible in isolation. For tokens whose ETH price is significantly lower than rsETH's ETH price, the threshold rises proportionally, but still remains in the sub-cent range under realistic oracle values.

**Impact classification: Low — contract fails to deliver promised returns, but the value lost per incident is dust-level.**

### Likelihood Explanation

Any unprivileged depositor can trigger this by calling `deposit(token, amount, referralId)` with a sufficiently small `amount`. No special role, no front-running, and no second error is required. The only prerequisite is that the deposited amount is below the truncation threshold. This can happen accidentally (e.g., a UI rounding error, a test transaction, or a contract integration that computes a residual amount). Likelihood is low-to-medium given that normal users deposit meaningful amounts, but the path is fully reachable with zero barriers.

### Recommendation

Add a zero-output guard immediately after computing `rsETHAmount` in every `deposit` function and in `viewSwapRsETHAmountAndFee`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount(); // or a dedicated error: ZeroRsETHOutput()
```

Alternatively, expose a `minRsETHAmountExpected` parameter (analogous to `minRSETHAmountExpected` already present in `LRTDepositPool.depositAsset`) so callers can enforce their own slippage floor. [7](#0-6) 

### Proof of Concept

Assume:
- `rsETHToETHrate = 1.05e18` (rsETH trades at a 5 % premium to ETH)
- `tokenToETHRate = 1e18` (wstETH ≈ 1 ETH)
- `feeBps = 0`

Call on `RSETHPoolNoWrapper` (Unichain):

```
deposit(wstETH, 1 wei, "")
```

Execution trace:
1. `amount = 1`, passes `if (amount == 0)` check. [8](#0-7) 
2. `safeTransferFrom(msg.sender, address(this), 1)` — 1 wei of wstETH leaves the user. [9](#0-8) 
3. `fee = 1 * 0 / 10_000 = 0`; `amountAfterFee = 1`.
4. `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation). [10](#0-9) 
5. `feeEarnedInToken[wstETH] += 0`.
6. `rsETH.safeTransfer(msg.sender, 0)` — user receives nothing. [11](#0-10) 
7. Transaction succeeds; user has lost 1 wei of wstETH with no recourse.

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L307-329)
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```
