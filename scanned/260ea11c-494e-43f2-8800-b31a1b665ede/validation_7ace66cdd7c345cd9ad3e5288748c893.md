### Title
ETH Dust Deposits Permanently Frozen Due to Missing Minimum rsETH Output Check - (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
The `deposit(string)` function in `RSETHPoolNoWrapper` (and the analogous ETH deposit functions in `RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`) accepts ETH from any caller but performs no check that the computed `rsETHAmount` is greater than zero. When a user deposits a dust amount of ETH (e.g., 1 wei) whose value, after fee deduction and rate conversion, rounds to zero via integer division, the contract silently transfers 0 rsETH to the user while retaining the deposited ETH permanently. No user-facing recovery path exists.

### Finding Description
In `RSETHPoolNoWrapper.deposit(string)`:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    if (!isEthDepositEnabled) revert EthDepositDisabled();
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

    feeEarnedInETH += fee;

    rsETH.safeTransfer(msg.sender, rsETHAmount);   // succeeds silently when rsETHAmount == 0

    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

The rate computation in `viewSwapRsETHAmountAndFee`:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

When `amountAfterFee` (in wei) is smaller than `rsETHToETHrate / 1e18` (which equals the rsETH/ETH exchange rate, currently > 1), the division truncates to zero. For example, with `rsETHToETHrate = 1.05e18` and `feeBps = 0`, depositing 1 wei yields `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`. ERC-20's `transfer(address, 0)` is valid and does not revert, so the call succeeds. The deposited ETH is absorbed into the pool's balance with no per-user accounting and no user-accessible withdrawal function.

The only functions that move ETH out of the pool are `bridgeAssetsViaNativeBridge()`, `bridgeAssets()`, and `withdrawFees()`, all restricted to `BRIDGER_ROLE`. There is no user-facing refund or recovery path, making the loss permanent.

The same pattern exists in:
- `RSETHPool.deposit(string)` [1](#0-0) 
- `RSETHPoolV3.deposit(string)` [2](#0-1) 
- `RSETHPoolV3ExternalBridge.deposit(string)` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.deposit(string)` [4](#0-3) 

The root cause in `RSETHPoolNoWrapper`: [5](#0-4) 

The rate formula that truncates to zero: [6](#0-5) 

The absence of any user-facing ETH recovery function: [7](#0-6) 

### Impact Explanation
A user who sends a dust ETH amount (e.g., 1 wei) to any of the pool `deposit()` functions receives 0 rsETH while their ETH is permanently retained by the pool. The ETH is eventually bridged to L1 as undifferentiated pool liquidity, with no mechanism for the depositor to reclaim it. This is a permanent freeze of the deposited funds. The financial magnitude per incident is negligible (1–2 wei), placing this in the **Low** impact tier: the contract fails to deliver its promised return (rsETH) without providing any refund path.

### Likelihood Explanation
Any unprivileged depositor can trigger this by sending a sufficiently small ETH value. The only guard is `if (amount == 0) revert InvalidAmount()`, which does not prevent 1-wei deposits. Because rsETH consistently trades above 1 ETH (rate > 1e18), the condition `rsETHAmount == 0` is always reachable for 1-wei deposits. No special state or timing is required.

### Recommendation
Add a post-computation check that reverts if `rsETHAmount` is zero, analogous to the `minRSETHAmountExpected` slippage guard used in `LRTDepositPool.depositETH`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, enforce a `minAmountToDeposit` threshold (as `LRTDepositPool` does) to prevent dust deposits from reaching the rate computation.

### Proof of Concept
1. `rsETHToETHrate` = 1.05e18 (rsETH worth 1.05 ETH, a realistic value).
2. `feeBps` = 0 (or any value; fee on 1 wei rounds to 0).
3. User calls `RSETHPoolNoWrapper.deposit{value: 1}("")`.
4. `viewSwapRsETHAmountAndFee(1)` computes: `fee = 0`, `amountAfterFee = 1`, `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`.
5. `feeEarnedInETH += 0` (no change).
6. `rsETH.safeTransfer(msg.sender, 0)` — succeeds, user receives 0 rsETH.
7. The 1 wei is now part of `address(this).balance` with no per-user record.
8. No user-callable function exists to recover it; it will be swept to L1 by the bridger.

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

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
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
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
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
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-301)
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L382-413)
```text
    function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw fees in ETH
        uint256 amountToSendInETH = feeEarnedInETH;
        feeEarnedInETH = 0;
        (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
        if (!success) revert TransferFailed();

        emit FeesWithdrawn(amountToSendInETH);
    }

    /// @dev Withdraws fees earned by the pool
    function withdrawFees(
        address receiver,
        address token
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw fees in ETH
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
    }

    /// @dev Legacy function - Withdraws assets from the contract for bridging
    function moveAssetsForBridging() external view onlyRole(BRIDGER_ROLE) {
        revert DeprecatedFunction();
    }
```
