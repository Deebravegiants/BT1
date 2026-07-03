### Title
Missing Minimum rsETH Output Guard in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPool.sol)

---

### Summary
All L2 pool `deposit()` functions accept an exact input amount but provide no `minRsETHAmount` parameter, leaving depositors with no protection against receiving fewer rsETH tokens than previewed when the oracle rate changes between transaction submission and execution.

---

### Finding Description

Every L2 pool variant implements `deposit()` with the same pattern:

1. Accept input (ETH or ERC20)
2. Compute output via `viewSwapRsETHAmountAndFee()`, which reads the live oracle rate
3. Transfer rsETH to the caller — with no minimum output check

`RSETHPool.sol` ETH deposit: [1](#0-0) 

`RSETHPool.sol` token deposit: [2](#0-1) 

The rate used in the calculation: [3](#0-2) 

The same pattern is present in every other L2 pool: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

By contrast, the L1 `LRTDepositPool` enforces a caller-supplied `minRSETHAmountExpected` on every deposit path: [8](#0-7) [9](#0-8) 

The rsETH oracle rate (`getRate()`) is a monotonically increasing value — it rises continuously as EigenLayer staking rewards accrue. Any depositor who previews the swap with `viewSwapRsETHAmountAndFee()` and then submits a `deposit()` transaction will receive fewer rsETH than shown if the rate ticks upward before the transaction is mined. There is no on-chain mechanism to reject the transaction in that case.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

The depositor's ETH/token value is preserved (rsETH received is worth the same ETH at the new rate), but the number of rsETH units received is lower than the amount shown by the view function. A user who needed a precise rsETH amount — e.g., to meet a collateral threshold in a DeFi protocol — cannot guarantee that amount will be delivered. The L1 deposit pool already recognises this risk and guards against it; the L2 pools do not.

---

### Likelihood Explanation

**Medium.** The rsETH rate increases on every block that accrues rewards. Any depositor who previews the swap and submits a transaction faces this discrepancy. The gap widens during periods of network congestion where transactions sit in the mempool for multiple blocks. No special attacker action is required — the rate drift is a normal, continuous protocol behaviour.

---

### Recommendation

Add a `minRsETHAmount` parameter to all `deposit()` overloads in every L2 pool contract (`RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) and revert if the computed `rsETHAmount` falls below it, mirroring the `minRSETHAmountExpected` guard already present in `LRTDepositPool`.

```solidity
// Example fix for RSETHPool.deposit(string)
function deposit(string memory referralId, uint256 minRsETHAmount)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
    ...
}
```

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` → sees they will receive `X` rsETH at the current rate `R`.
2. User submits `deposit{value: 1 ether}(referralId)`.
3. Before the transaction is mined, the oracle rate increases from `R` to `R'` (normal reward accrual).
4. `viewSwapRsETHAmountAndFee` inside the transaction now computes `X' = 1e18 * 1e18 / R'` where `R' > R`, so `X' < X`.
5. User receives `X'` rsETH — fewer than previewed — with no on-chain protection and no revert.

The same sequence applies to token deposits via `deposit(address token, uint256 amount, string memory referralId)` across all five affected pool contracts. [3](#0-2) [8](#0-7)

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

**File:** contracts/pools/RSETHPool.sol (L311-320)
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

**File:** contracts/pools/RSETHPoolV3.sol (L248-265)
```text
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L229-244)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
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
