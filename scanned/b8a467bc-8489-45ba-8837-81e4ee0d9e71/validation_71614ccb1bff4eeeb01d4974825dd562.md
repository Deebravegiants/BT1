### Title
No Slippage Protection in L2 Pool `deposit` Functions Allows Users to Receive Fewer rsETH Than Expected - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

All L2 deposit pool contracts expose public `deposit` functions that mint rsETH/wrsETH to users based on a live oracle rate, but accept no `minRsETHAmount` parameter. Users have no on-chain mechanism to bound the minimum output they will receive. The L1 `LRTDepositPool` correctly implements this protection via `minRSETHAmountExpected`, but the L2 pools do not.

---

### Finding Description

The L2 pool contracts (`RSETHPoolV3`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3WithNativeChainBridge`) all expose deposit entry points of the form:

```solidity
// RSETHPoolV3.sol L246-265
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(...) {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}

// RSETHPoolV3.sol L271-293
function deposit(address token, uint256 amount, string memory referralId) external nonReentrant whenNotPaused ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

The `rsETHAmount` is computed entirely from the live oracle rate at execution time:

```solidity
// RSETHPoolV3.sol L299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

There is no parameter allowing the caller to specify a minimum acceptable output. The same pattern is replicated identically in `RSETHPool.sol` (L265-305), `RSETHPoolNoWrapper.sol` (L231-271), and `RSETHPoolV3WithNativeChainBridge.sol` (L282-329).

By contrast, the L1 `LRTDepositPool` correctly guards both entry points:

```solidity
// LRTDepositPool.sol L76-93
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...

// LRTDepositPool.sol L99-118
function depositAsset(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected, ...) external ...
```

The oracle rate (`rsETHOracle`) is a cross-chain rate that is updated periodically by operators. Between the moment a user signs and broadcasts a deposit transaction and the moment it is included in a block, the oracle rate can change — either through a legitimate operator update or through natural block-ordering effects. Because the user cannot specify a floor on the rsETH they will receive, they have no protection against this.

---

### Impact Explanation

A depositor sends ETH or a supported LST token to an L2 pool and receives fewer rsETH/wrsETH than they observed when constructing the transaction, with no on-chain recourse. The deposited asset is fully transferred to the pool; the shortfall in rsETH output is unrecoverable. This matches the **Low** impact class: *"Contract fails to deliver promised returns, but doesn't lose value"* — the user's deposited collateral is not stolen, but the rsETH minted is less than the rate the user observed and intended to transact at.

If the oracle rate is updated in the same block as a pending deposit (a realistic scenario on L2s where block times are short and oracle updates are frequent), the user silently receives a worse exchange rate with no ability to revert.

---

### Likelihood Explanation

The likelihood is **Medium**. L2 oracle rates for rsETH are updated periodically by operators. On chains with short block times (Arbitrum, Optimism, Base), a deposit transaction submitted at one rate can easily be included after an oracle update in the same or next block. No attacker action is required — the rate drift is a natural consequence of the oracle update cadence. Any user depositing a non-trivial amount is exposed on every transaction.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to all L2 pool `deposit` functions, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert SlippageExceeded();
    wrsETH.mint(msg.sender, rsETHAmount);
    ...
}
```

Apply the same fix to the token-deposit overload and to all affected pool variants.

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes `rsETHAmount = X`.
2. User submits `deposit{value: 1 ether}("ref")` targeting `RSETHPoolV3`.
3. Before the transaction is mined, the operator calls `setRate(newRate)` on `rsETHOracle`, increasing the rsETH/ETH rate (i.e., rsETH is now worth more ETH per unit, so fewer rsETH are minted per ETH deposited).
4. User's transaction executes: `viewSwapRsETHAmountAndFee` now returns `rsETHAmount = Y < X`.
5. User receives `Y` wrsETH instead of `X`, with no revert and no recourse.
6. The gap `X - Y` represents value the user expected but did not receive, permanently lost to the rate change.

Relevant code paths: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-329)
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

**File:** contracts/LRTDepositPool.sol (L76-118)
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

    /// @notice helps user stake LST to the protocol
    /// @param asset LST asset address to stake
    /// @param depositAmount LST asset amount to stake
    /// @param minRSETHAmountExpected Minimum amount of rseth to receive
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
