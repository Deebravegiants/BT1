### Title
Missing Minimum rsETH Output Protection in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, RSETHPoolV2ExternalBridge.sol, RSETHPool.sol, RSETHPoolNoWrapper.sol)

---

### Summary

The `deposit()` functions across all L2 pool contracts accept ETH or supported tokens and return rsETH/wrsETH calculated from an on-chain oracle rate, but provide no `minRsETHAmount` parameter for the caller to enforce a minimum acceptable output. The L1 `LRTDepositPool` correctly implements this protection via `minRSETHAmountExpected`, but the L2 equivalents do not.

---

### Finding Description

Every L2 pool contract exposes one or two `deposit()` entry points that are callable by any unprivileged user:

**RSETHPoolV3ExternalBridge.sol** (representative example):
```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER) {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The rsETH amount is computed entirely from the oracle rate with no floor enforced by the caller:
```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

The same pattern exists in:
- `RSETHPoolV2ExternalBridge.deposit(string)` [3](#0-2) 
- `RSETHPool.deposit(string)` and `RSETHPool.deposit(address,uint256,string)` [4](#0-3) 
- `RSETHPoolNoWrapper.deposit(string)` and `RSETHPoolNoWrapper.deposit(address,uint256,string)` [5](#0-4) 

By contrast, the L1 `LRTDepositPool` correctly enforces a caller-supplied minimum:
```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) ...
``` [6](#0-5) 

with the check:
```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [7](#0-6) 

---

### Impact Explanation

A user calls `viewSwapRsETHAmountAndFee()` off-chain to preview the rsETH they will receive, then submits a `deposit()` transaction. If the oracle rate is updated (legitimately, by the admin) between the preview and the transaction's execution — increasing the rsETH/ETH rate — the user receives fewer rsETH tokens than previewed, with no on-chain protection. The user's ETH/token is fully consumed and they receive a smaller rsETH amount than they agreed to. This matches the **Low** impact class: *contract fails to deliver promised returns, but doesn't lose value*.

---

### Likelihood Explanation

The oracle rate for rsETH/ETH is updated periodically by the protocol. Any depositor who previews the swap and submits a transaction during a period of oracle rate movement is exposed. This is a normal operational condition, not a rare edge case, and affects all L2 chains where these pool contracts are deployed.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to all `deposit()` functions in the L2 pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused ...
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV3ExternalBridge` and sees they will receive `X` wrsETH at the current oracle rate.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction is mined, the admin updates the oracle to a higher rsETH/ETH rate (rsETH appreciated).
4. The transaction executes: `rsETHAmount = 1e18 * 1e18 / newHigherRate` → user receives `Y < X` wrsETH.
5. No revert occurs; the user has no recourse. The gap between `X` and `Y` is silently absorbed. [1](#0-0) [3](#0-2) [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/pools/RSETHPool.sol (L265-305)
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

    /// @dev Swaps token for rsETH
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-271)
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

    /// @dev Swaps token for rsETH
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
