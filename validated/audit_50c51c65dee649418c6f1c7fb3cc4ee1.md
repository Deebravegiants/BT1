### Title
Missing Slippage Protection in `deposit()` Functions Allows Users to Receive Fewer rsETH Tokens Than Expected - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol)

---

### Summary

All `deposit()` functions across the LRT-rsETH L2 pool contracts accept ETH or supported tokens and mint/transfer rsETH to the caller based on a live oracle rate, but none of them accept a `minAmountOut` (minimum rsETH) parameter. A user who submits a deposit transaction has no on-chain guarantee about the minimum rsETH they will receive, because the oracle rate can be updated between transaction submission and execution.

---

### Finding Description

Every pool contract exposes one or two `deposit()` overloads for unprivileged callers:

**RSETHPoolV3ExternalBridge.sol** (ETH path):
```solidity
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // ← no minAmountOut check
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

The rsETH amount is computed entirely from the live oracle rate at execution time:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // ← live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

The same pattern is present in:
- `RSETHPool.sol` `deposit(string)` and `deposit(address,uint256,string)`
- `RSETHPoolV2ExternalBridge.sol` `deposit(string)`
- `RSETHPoolV3ExternalBridge.sol` `deposit(string)` and `deposit(address,uint256,string)`
- `RSETHPoolNoWrapper.sol` `deposit(string)` and `deposit(address,uint256,string)`

None of these functions accept or enforce a caller-supplied minimum rsETH output.

---

### Impact Explanation

The rsETH/ETH oracle rate is not static. It is updated by an off-chain oracle operator to reflect the current L1 exchange rate (which increases as staking rewards accrue, and can also jump on oracle refresh). If the oracle is updated between the moment a user signs and broadcasts a deposit transaction and the moment that transaction is included in a block, the user receives fewer rsETH tokens than they observed when constructing the transaction. The user's ETH (or token) is fully consumed by the pool with no recourse. Because the contract provides a `viewSwapRsETHAmountAndFee` preview function, users naturally rely on it to estimate their output — but there is no mechanism to enforce that estimate at execution time.

Impact classification: **Low — Contract fails to deliver the promised/previewed return, but the user does not lose their principal in absolute terms (they receive some rsETH, just less than expected).**

---

### Likelihood Explanation

Oracle updates for rsETH/ETH occur regularly (every few hours or on significant rate changes). On L2 networks, user transactions can sit in the mempool or be delayed by sequencer ordering. The combination of frequent oracle refreshes and variable transaction inclusion latency makes it realistic that a deposit transaction is executed at a different rate than the user previewed. Any unprivileged depositor calling `deposit()` is exposed to this condition on every transaction.

---

### Recommendation

Add a `minRsETHAmountOut` parameter to all `deposit()` functions and revert if the computed rsETH amount falls below it:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountOut)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
+   if (rsETHAmount < minRsETHAmountOut) revert InsufficientOutput();

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same change to the token-deposit overload and to all other pool contracts listed above.

---

### Proof of Concept

1. Oracle currently reports `rsETHToETHrate = 1.05e18` (1 rsETH = 1.05 ETH).
2. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `≈ 0.952 rsETH`.
3. User submits `deposit{value: 1 ether}("ref")`.
4. Before the transaction is included, the oracle is updated to `rsETHToETHrate = 1.10e18`.
5. The transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 rsETH` — the user receives ~4.5% fewer rsETH tokens than previewed, with no on-chain protection and no ability to revert.

**Relevant code locations:**

`RSETHPoolV3ExternalBridge.sol` — ETH deposit, no `minAmountOut`: [1](#0-0) 

`RSETHPoolV3ExternalBridge.sol` — token deposit, no `minAmountOut`: [2](#0-1) 

`RSETHPoolV3ExternalBridge.sol` — live oracle rate used at execution time: [3](#0-2) 

`RSETHPool.sol` — same pattern, ETH deposit: [4](#0-3) 

`RSETHPool.sol` — same pattern, token deposit: [5](#0-4) 

`RSETHPoolNoWrapper.sol` — same pattern, ETH deposit: [6](#0-5) 

`RSETHPoolNoWrapper.sol` — same pattern, token deposit: [7](#0-6) 

`RSETHPoolV2ExternalBridge.sol` — same pattern, ETH deposit: [8](#0-7)

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
