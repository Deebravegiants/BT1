### Title
`deposit()` Functions in L2 Pool Contracts Lack Slippage Protection, Allowing Users to Receive Fewer wrsETH Than Expected - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `deposit()` functions across all L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, `RSETHPoolNoWrapper`) compute the output wrsETH amount at execution time using the live oracle rate, but accept no `minOutputAmount` parameter. A user who previews the swap and submits a transaction can receive fewer wrsETH tokens than expected if the oracle rate updates before the transaction executes.

### Finding Description
Every L2 pool `deposit()` function computes the output amount as:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

where `rsETHToETHrate = getRate()` is fetched live from the oracle at execution time. If the rsETH/ETH rate increases between the user's off-chain preview and on-chain execution, `rsETHAmount` decreases proportionally. There is no guard of the form `require(rsETHAmount >= minOutputAmount)`.

This is in direct contrast to the mainnet `LRTDepositPool`, which explicitly accepts and enforces a `minRSETHAmountExpected` parameter in both `depositETH()` and `depositAsset()`.

The affected `deposit()` functions are:

- `RSETHPoolV3.deposit(string)` — ETH path [1](#0-0) 
- `RSETHPoolV3.deposit(address,uint256,string)` — token path [2](#0-1) 
- `RSETHPoolV3ExternalBridge.deposit(string)` and `deposit(address,uint256,string)` [3](#0-2) 
- `RSETHPoolV3WithNativeChainBridge.deposit(string)` and `deposit(address,uint256,string)` [4](#0-3) 
- `RSETHPool.deposit(string)` and `deposit(address,uint256,string)` [5](#0-4) 
- `RSETHPoolNoWrapper.deposit(string)` and `deposit(address,uint256,string)` [6](#0-5) 

The rate-dependent output calculation that is unguarded: [7](#0-6) 

The mainnet counterpart that correctly enforces slippage: [8](#0-7) 

### Impact Explanation
**Low.** The user does not lose ETH value — the wrsETH they receive is worth the ETH they deposited at the updated rate. However, the contract fails to deliver the number of wrsETH tokens the user expected when they previewed the transaction. This can break downstream interactions where the user needed a minimum token count (e.g., to satisfy a collateral threshold in another protocol, or to meet a minimum for a subsequent bridge/wrap operation). The user has no on-chain mechanism to protect against receiving fewer tokens than anticipated.

### Likelihood Explanation
**Medium.** The rsETH/ETH oracle rate is updated periodically (it monotonically increases as staking rewards accrue). Any user whose transaction sits in the mempool across an oracle rate update will receive fewer wrsETH than previewed. On L2 chains with public mempools or during periods of network congestion, this is a realistic and recurring scenario.

### Recommendation
Add a `minOutputAmount` parameter to all `deposit()` overloads in the L2 pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```diff
- function deposit(string memory referralId) external payable nonReentrant whenNotPaused ...
+ function deposit(string memory referralId, uint256 minRsETHAmount) external payable nonReentrant whenNotPaused ...
  {
      ...
      (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
+     if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
      ...
      wrsETH.mint(msg.sender, rsETHAmount);
  }
```

Apply the same pattern to the token-path `deposit(address,uint256,string)` overload in all affected pool contracts.

### Proof of Concept
1. User calls `RSETHPoolV3.viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `X` wrsETH at the current oracle rate `R`.
2. User submits `deposit{value: 1 ether}(referralId)`.
3. Before the transaction is included, the rsETH oracle rate updates from `R` to `R'` where `R' > R` (rsETH has accrued more staking rewards).
4. The transaction executes: `rsETHAmount = 1e18 * 1e18 / R'` which is strictly less than `X`.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
6. User receives fewer wrsETH than expected with no recourse. [9](#0-8)

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-270)
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
