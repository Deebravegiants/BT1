### Title
Missing Deadline and Minimum Output Parameters in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

The `deposit()` functions across all L2 pool contracts accept ETH or supported LSTs and mint `wrsETH`/`rsETH` to the caller, but provide no deadline parameter and no minimum output (`minRsETHAmount`) parameter. A user's pending transaction can be executed at an arbitrarily later time when the oracle-reported rsETH/ETH rate has moved unfavorably, and the user has no on-chain mechanism to prevent this.

---

### Finding Description

Every L2 pool variant exposes two public `deposit` overloads — one for native ETH and one for ERC-20 LSTs — that compute the output amount solely from the live oracle rate at execution time:

**`RSETHPoolV3.sol` (ETH path):**
```solidity
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

**`RSETHPoolV3.sol` (token path):**
```solidity
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused
    onlySupportedToken(token) limitDailyMint(amount, token)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}
``` [2](#0-1) 

The output is computed as:
```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [3](#0-2) 

Neither overload accepts a `minRsETHAmount` nor a `deadline` parameter. The identical pattern is present in `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV3ExternalBridge.sol`: [4](#0-3) [5](#0-4) [6](#0-5) 

By contrast, the L1 `LRTDepositPool` does accept a `minRSETHAmountExpected` slippage guard: [7](#0-6) 

The L2 pool contracts provide neither protection.

---

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who submits a `deposit` transaction during a period of network congestion may have their transaction included in a block significantly later than intended. During that delay, the rsETH oracle rate (`getRate()`) may have increased (rsETH appreciates as staking rewards accrue). When the transaction finally executes, the user receives fewer `wrsETH` tokens than the rate at submission time would have yielded. The user's ETH/LST is consumed in full; they simply receive less output than they anticipated. There is no mechanism — neither a deadline nor a minimum output floor — to revert the transaction in this scenario.

---

### Likelihood Explanation

**Likelihood: High.**

L2 networks (Arbitrum, Optimism, Unichain, etc.) can experience sequencer delays, reorgs, or periods of elevated gas prices that cause transactions to remain pending for extended periods. The rsETH oracle rate is updated periodically by the protocol; any update that occurs between a user's transaction submission and its inclusion will silently reduce the user's output. No special attacker action is required — ordinary network conditions are sufficient to trigger this outcome for any depositor.

---

### Recommendation

1. Add a `uint256 deadline` parameter to both `deposit` overloads in all L2 pool contracts and revert if `block.timestamp > deadline`.
2. Add a `uint256 minRsETHAmount` parameter and revert if the computed `rsETHAmount < minRsETHAmount`.

Example for `RSETHPoolV3.sol`:
```solidity
function deposit(string memory referralId, uint256 minRsETHAmount, uint256 deadline)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    if (block.timestamp > deadline) revert DeadlineExpired();
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
    ...
}
```

---

### Proof of Concept

1. Alice calls `RSETHPoolV3.deposit{value: 1 ether}("ref")` when the oracle rate is `1.05 ETH/rsETH`, expecting ≈ `0.952 wrsETH`.
2. The transaction sits in the L2 sequencer queue due to congestion.
3. The protocol oracle updates the rate to `1.10 ETH/rsETH` before Alice's transaction is included.
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 wrsETH`.
5. Alice receives `~0.909 wrsETH` instead of `~0.952 wrsETH` — a ~4.5% shortfall — with no on-chain recourse, because neither a deadline nor a minimum output check exists. [3](#0-2)

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
