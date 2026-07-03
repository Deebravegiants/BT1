### Title
Missing Slippage Protection in `deposit()` Functions Allows Users to Receive Fewer rsETH Than Expected - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
All L2 pool `deposit()` functions lack a `minRSETHAmountExpected` parameter. Users have no on-chain protection against receiving fewer rsETH than expected if the oracle rate changes between transaction submission and execution. The L1 `LRTDepositPool` already implements this protection, but none of the L2 pool variants do.

### Finding Description
The `deposit(string)` and `deposit(address, uint256, string)` functions in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, and `RSETHPoolNoWrapper` all compute the rsETH output amount at execution time using the live oracle rate, with no caller-supplied minimum output guard.

In `RSETHPoolV3.deposit(string)`: [1](#0-0) 

The rsETH amount is computed entirely from the oracle rate at the moment of execution: [2](#0-1) 

The same pattern is present in the token deposit variant: [3](#0-2) 

And identically in `RSETHPoolV3ExternalBridge.deposit()`: [4](#0-3) 

And in `RSETHPoolNoWrapper.deposit()`: [5](#0-4) 

By contrast, the L1 `LRTDepositPool` already enforces a minimum output check via `minRSETHAmountExpected`: [6](#0-5) 

The check is enforced in `_beforeDeposit`: [7](#0-6) 

The L2 oracle rate (`getRate()`) is sourced from a cross-chain rate provider that is updated periodically. On L2 chains, transactions can sit in the mempool for multiple blocks. If a rate update is applied between submission and execution, the user silently receives fewer rsETH than they observed when constructing the transaction.

### Impact Explanation
**Low.** The user receives fewer rsETH than expected for their deposited ETH or LST. The protocol does not lose value — the deposited assets are correctly accounted for — but the user's position is worse than they intended. This matches the allowed scope: "Contract fails to deliver promised returns, but doesn't lose value."

### Likelihood Explanation
**Medium.** The rsETH/ETH oracle rate on L2 is updated by a cross-chain rate provider on a regular schedule. Any deposit transaction that is pending in the mempool when a rate update lands will execute at the new (higher) rate, yielding fewer rsETH. This is a normal operating condition, not an edge case, and affects every L2 pool variant deployed by the protocol.

### Recommendation
Add a `minRSETHAmountExpected` parameter to all `deposit()` overloads in every L2 pool contract (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `RSETHPoolNoWrapper`), mirroring the pattern already used in `LRTDepositPool._beforeDeposit()`. Revert if the computed rsETH amount is below the caller-supplied minimum.

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV3` and observes they will receive `X` rsETH at the current oracle rate.
2. User submits `deposit{value: 1 ether}(referralId)`.
3. Before the transaction is included, the cross-chain rate provider updates the oracle: `rsETHToETHrate` increases from `R` to `R'` where `R' > R`.
4. The transaction executes. `rsETHAmount = (1 ether - fee) * 1e18 / R'`, which is strictly less than `X`.
5. User receives fewer rsETH than observed in step 1 with no revert and no recourse, because there is no minimum output check anywhere in the call path. [8](#0-7)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
