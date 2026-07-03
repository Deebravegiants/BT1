### Title
Lack of Minimum Output Protection in `deposit` Functions Across L2 Pool Contracts - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, RSETHPoolV3.sol, RSETHPool.sol, RSETHPoolNoWrapper.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV2.sol, RSETHPoolV2NBA.sol, RSETHPoolV3WithNativeChainBridge.sol)

### Summary

Every user-facing `deposit` function across the L2 pool family computes the rsETH/wrsETH output amount from a live oracle rate at execution time but accepts no `minRsETHAmount` parameter. A user who previews the swap off-chain and then submits the transaction can receive materially fewer rsETH than expected if the oracle rate is updated before the transaction is mined. The L1-side `LRTDepositPool` already enforces this protection via `minRSETHAmountExpected`, making the omission in the L2 pools an inconsistency with an established design pattern in the same codebase.

### Finding Description

All L2 pool contracts expose public `deposit` functions that:

1. Accept ETH or an ERC-20 token from the caller.
2. Call `getRate()` on the configured oracle to obtain the live rsETH/ETH exchange rate.
3. Compute `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` (or the token-denominated equivalent).
4. Mint or transfer that amount of rsETH/wrsETH to the caller.

No step allows the caller to specify a minimum acceptable output. Representative examples:

**`RSETHPoolV3ExternalBridge.deposit(string)` (ETH path)** [1](#0-0) 

**`RSETHPoolV3ExternalBridge.deposit(address,uint256,string)` (token path)** [2](#0-1) 

**`RSETHPool.deposit(string)` (ETH path)** [3](#0-2) 

**`RSETHPool.deposit(address,uint256,string)` (token path)** [4](#0-3) 

**`RSETHPoolNoWrapper.deposit(string)` (ETH path)** [5](#0-4) 

**`RSETHPoolNoWrapper.deposit(address,uint256,string)` (token path)** [6](#0-5) 

The same pattern is present in `RSETHPoolV2.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV2NBA.sol`, and `RSETHPoolV3WithNativeChainBridge.sol`. [7](#0-6) [8](#0-7) 

The oracle rate is fetched at execution time: [9](#0-8) 

By contrast, the L1 `LRTDepositPool` enforces a caller-supplied minimum: [10](#0-9) [11](#0-10) 

### Impact Explanation

If the oracle rate is updated (legitimately, e.g. after a rebase or a scheduled oracle push) between the moment a user previews the swap and the moment the transaction is mined, the user receives fewer rsETH/wrsETH than they were shown. The user's ETH or tokens are consumed in full; only the output is reduced. This matches the allowed impact category: **"Contract fails to deliver promised returns, but doesn't lose value"** (Low).

### Likelihood Explanation

The rsETH/ETH oracle rate increases monotonically as staking rewards accrue, so the rate change direction is predictable. On chains with longer block times or during periods of high mempool congestion, the window between preview and execution is wider. Any oracle update that lands in that window silently reduces the user's output with no on-chain revert or warning. The entry path is fully permissionless: any depositor calling `deposit` is affected.

### Recommendation

Add a `uint256 minRsETHAmount` parameter to every `deposit` overload in all L2 pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount)
    external payable nonReentrant whenNotPaused ...
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert MinimumAmountToReceiveNotMet();
    ...
}
```

Apply the same pattern to the token-denominated `deposit(address token, uint256 amount, string memory referralId, uint256 minRsETHAmount)` overloads.

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `X` wrsETH at the current oracle rate.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction is mined, the oracle is updated (rate increases, meaning rsETH is worth more ETH per unit).
4. The transaction executes: `rsETHAmount = 1e18 * 1e18 / newHigherRate` → user receives `X' < X` wrsETH.
5. No revert occurs; the user silently receives fewer tokens than previewed, with no recourse.

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
