### Title
Precision Loss in `viewSwapRsETHAmountAndFee()` Causes User to Lose Token Deposit While Receiving Zero wrsETH - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
In all L2 pool contracts, the token-variant of `viewSwapRsETHAmountAndFee()` computes `rsETHAmount` via integer division without a zero-output guard. When a user deposits a sufficiently small token amount, the division truncates to zero. The deposit function then takes the user's tokens but transfers or mints zero wrsETH in return, permanently losing the user's funds to the pool.

### Finding Description
Every pool contract computes the rsETH output for a token deposit as:

```solidity
// RSETHPool.sol L346, RSETHPoolV3.sol L334, RSETHPoolV3ExternalBridge.sol L452, etc.
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Because Solidity integer division truncates, if `amountAfterFee * tokenToETHRate < rsETHToETHrate`, then `rsETHAmount = 0`.

The deposit function then proceeds unconditionally:

**RSETHPool.sol (Arbitrum)**
```solidity
// L296-304
IERC20(token).safeTransferFrom(msg.sender, address(this), amount); // tokens taken
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount); // transfers 0 — succeeds silently
```

**RSETHPoolV3.sol / RSETHPoolV3ExternalBridge.sol / RSETHPoolV3WithNativeChainBridge.sol**
```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), amount); // tokens taken
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount); // mints 0 — outcome depends on mint impl
```

There is no `if (rsETHAmount == 0) revert` guard anywhere in the deposit path. The only zero-check is `if (amount == 0) revert InvalidAmount()`, which guards the input amount, not the computed output.

**Concrete trigger condition**: With `tokenToETHRate = 1e18` (e.g., stETH ≈ 1 ETH) and `rsETHToETHrate = 1.05e18` (rsETH has appreciated), depositing `amountAfterFee = 1` wei of stETH yields:
```
rsETHAmount = 1 * 1e18 / 1.05e18 = 0
```
The user's 1 wei of stETH is permanently absorbed by the pool.

### Impact Explanation
**Low — Contract fails to deliver promised returns.**

The user deposits a non-zero token amount and receives zero wrsETH. In `RSETHPool.sol`, `safeTransfer(msg.sender, 0)` is a no-op that succeeds silently under standard ERC-20 semantics, making the fund loss certain. The user's tokens are permanently retained by the pool (credited to the pool's general balance, not even to `feeEarnedInToken`). The practical loss per transaction is tiny (sub-wei to a few wei of an LST), but the contract silently violates its core invariant: every non-zero deposit must yield a non-zero rsETH output.

### Likelihood Explanation
**Low.** A user must deposit an amount small enough that `amountAfterFee * tokenToETHRate < rsETHToETHrate`. Given that rsETH rates are currently close to 1e18 and supported tokens (stETH, rETH) also have rates near 1e18, the threshold is approximately 1–2 wei of the deposited token. Normal users depositing meaningful amounts are unaffected. The risk increases if rsETH appreciates significantly relative to a supported token, raising the truncation threshold.

### Recommendation
Add an explicit zero-output guard in every pool's token deposit path, mirroring the pattern already used in `notifyRewardAmount` in `KernelDepositPool.sol`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount(); // add this guard
```

Alternatively, enforce a minimum deposit amount that guarantees at least 1 unit of rsETH output given the current oracle rates.

### Proof of Concept
1. Deploy or interact with `RSETHPool.sol` on Arbitrum (or any V3 pool) with a supported LST token.
2. Observe current rates: `rsETHToETHrate = 1.05e18`, `tokenToETHRate = 1e18`, `feeBps = 0`.
3. Call `deposit(token, 1, "")` — depositing 1 wei of the LST.
4. Inside `viewSwapRsETHAmountAndFee`: `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`.
5. `safeTransferFrom` moves 1 wei of LST from the caller to the pool.
6. `safeTransfer(msg.sender, 0)` executes successfully, transferring nothing.
7. Caller's 1 wei of LST is permanently lost; pool balance increases by 1 wei with no corresponding wrsETH minted. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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
