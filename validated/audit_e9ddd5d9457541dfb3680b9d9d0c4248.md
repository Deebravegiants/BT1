### Title
Lack of Slippage Protection in Pool `deposit()` Functions - (File: contracts/pools/RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV3.sol, RSETHPoolV3ExternalBridge.sol)

---

### Summary
Multiple L2 pool `deposit()` functions that swap ETH or LST tokens for rsETH/wrsETH lack a `minRsETHAmountExpected` parameter, meaning users have no way to specify a minimum acceptable output. If the oracle rate changes between transaction submission and execution, users receive fewer rsETH tokens than expected with no ability to revert.

---

### Finding Description

Every L2 pool `deposit()` function computes the rsETH output at execution time using a live oracle rate, but accepts no minimum-output parameter from the caller.

**`RSETHPool.deposit(string referralId)`** (ETH → wrsETH): [1](#0-0) 

**`RSETHPool.deposit(address token, uint256 amount, string referralId)`** (LST → wrsETH): [2](#0-1) 

**`RSETHPoolNoWrapper.deposit(string referralId)`** (ETH → rsETH): [3](#0-2) 

**`RSETHPoolNoWrapper.deposit(address token, uint256 amount, string referralId)`** (LST → rsETH): [4](#0-3) 

**`RSETHPoolV2.deposit(string referralId)`** (ETH → wrsETH): [5](#0-4) 

**`RSETHPoolV2ExternalBridge.deposit(string referralId)`** (ETH → wrsETH): [6](#0-5) 

**`RSETHPoolV3.deposit(string referralId)`** and **`RSETHPoolV3.deposit(address token, ...)`** (ETH/LST → wrsETH): [7](#0-6) 

**`RSETHPoolV3ExternalBridge.deposit(string referralId)`** and **`RSETHPoolV3ExternalBridge.deposit(address token, ...)`**: [8](#0-7) 

In every case, the rsETH output is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [9](#0-8) 

The `rsETHToETHrate` is fetched live from the oracle at execution time. There is no `minRsETHAmountExpected` guard.

**Contrast with `LRTDepositPool`**, which correctly implements slippage protection: [10](#0-9) 

The L1 deposit pool accepts `minRSETHAmountExpected` and reverts with `MinimumAmountToReceiveNotMet` if the minted amount falls short. The L2 pool contracts have no equivalent.

---

### Impact Explanation

A user depositing ETH or an LST token into any L2 pool receives however many rsETH/wrsETH tokens the oracle rate dictates at the moment of execution. If the oracle rate increases between broadcast and mining (rsETH appreciates in ETH terms), the user receives fewer rsETH tokens than they expected when they submitted the transaction. The user has no recourse: the transaction succeeds, their ETH/LST is consumed, and they receive a sub-expected rsETH amount. This constitutes the contract failing to deliver promised returns — the user loses value relative to their expectation at submission time.

**Impact:** Low — Contract fails to deliver promised returns, but doesn't lose value relative to the on-chain state at execution time. However, in volatile oracle conditions or with MEV manipulation of the oracle update ordering, the shortfall can be material.

---

### Likelihood Explanation

The oracle rate (`rsETHToETHrate`) is updated periodically. Any deposit transaction that is pending in the mempool when an oracle update is mined will execute at the new rate. This is a routine occurrence on all L2 chains where these pools are deployed (Arbitrum, Unichain, etc.). No special attacker capability is required — ordinary oracle updates are sufficient to trigger the issue for any pending deposit.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to all `deposit()` functions in the L2 pool contracts, mirroring the pattern already used in `LRTDepositPool._beforeDeposit()`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

The helper `getMinAmount(uint256 amount, uint256 slippageTolerance)` already exists in several pool contracts and can be used off-chain to compute the appropriate `minRsETHAmountExpected` value before submitting the transaction. [11](#0-10) 

---

### Proof of Concept

1. Oracle reports `rsETHToETHrate = 1.05e18` (1 rsETH = 1.05 ETH).
2. User submits `deposit{value: 1 ether}("ref")` to `RSETHPoolV2ExternalBridge`, expecting `~0.952 wrsETH` (after fee).
3. Before the tx is mined, the oracle updates to `rsETHToETHrate = 1.10e18`.
4. The deposit executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 wrsETH`.
5. User receives `~0.909 wrsETH` instead of `~0.952 wrsETH` — a ~4.5% shortfall — with no revert. [6](#0-5) [12](#0-11)

### Citations

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L307-316)
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

**File:** contracts/pools/RSETHPoolV3.sol (L246-293)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-412)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L540-544)
```text
    function getMinAmount(uint256 amount, uint256 slippageTolerance) external pure returns (uint256) {
        if (slippageTolerance > 10_000) revert InvalidSlippageTolerance();

        return amount - (amount * slippageTolerance / 10_000);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
