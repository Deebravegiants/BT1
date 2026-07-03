### Title
Missing Deadline Check in Pool `deposit` Functions Allows Stale Execution at Unfavorable Oracle Rate - (`contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV2.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

All L2 pool `deposit` functions that swap ETH or LST tokens for rsETH/wrsETH lack both a deadline parameter and a minimum-output parameter. A transaction submitted to the mempool can execute arbitrarily late, at which point the oracle-reported rsETH/ETH rate will have increased (rsETH is yield-bearing and monotonically appreciates), causing the user to receive fewer rsETH tokens than they expected at submission time, with no on-chain protection.

---

### Finding Description

Every user-facing `deposit` function across the L2 pool family accepts only an amount and a `referralId`. The rsETH output is computed at execution time by calling `viewSwapRsETHAmountAndFee`, which reads the live oracle rate via `getRate()`. Neither a `deadline` guard nor a `minRsETHAmountOut` parameter is present.

**RSETHPoolNoWrapper.sol – ETH deposit:** [1](#0-0) 

**RSETHPoolNoWrapper.sol – token deposit:** [2](#0-1) 

**RSETHPoolV3.sol – ETH deposit:** [3](#0-2) 

**RSETHPoolV3.sol – token deposit:** [4](#0-3) 

The rate used in all of these is fetched live from the oracle: [5](#0-4) 

The same pattern is repeated verbatim in `RSETHPoolV2.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV3ExternalBridge.sol`, and `RSETHPoolV3WithNativeChainBridge.sol`. [6](#0-5) 

By contrast, `LRTDepositPool.depositETH` on L1 does accept a `minRSETHAmountExpected` slippage guard, but the L2 pool contracts provide no equivalent protection: [7](#0-6) 

---

### Impact Explanation

rsETH is a yield-bearing token whose ETH-denominated rate increases monotonically over time. When a deposit transaction is delayed in the mempool (e.g., due to low gas price, network congestion, or validator ordering), the oracle rate will have risen by the time the transaction executes. The user receives fewer rsETH tokens than they anticipated at submission time. Because no minimum-output check exists in any of the pool contracts, the transaction succeeds silently and the user has no recourse.

The user does not lose ETH value in absolute terms, but they receive fewer rsETH than promised by the rate they observed when constructing the transaction, meaning they miss the yield accrual on the shortfall. This maps to the allowed impact: **Low – Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

This is reachable by any unprivileged depositor on any chain where these pool contracts are deployed. Ethereum L1 and L2 networks regularly experience mempool congestion. A user who submits a deposit with a low gas price during a congestion spike may have their transaction delayed by hours or days. The rsETH rate accrues continuously, so even a multi-hour delay produces a measurable shortfall. No special attacker capability is required; the harm is passive and automatic.

---

### Recommendation

1. Add a `uint256 deadline` parameter to every public `deposit` function and revert if `block.timestamp > deadline`.
2. Add a `uint256 minRsETHAmountOut` parameter and revert if the computed `rsETHAmount < minRsETHAmountOut`.

Example modifier pattern (analogous to Uniswap V2):
```solidity
modifier ensure(uint256 deadline) {
    require(deadline >= block.timestamp, "RSETHPool: EXPIRED");
    _;
}
```

Apply both protections to all `deposit` overloads in `RSETHPoolNoWrapper`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`.

---

### Proof of Concept

1. The rsETH/ETH oracle rate at block N is `1.05e18` (1 rsETH = 1.05 ETH).
2. Alice calls `RSETHPoolV3.deposit{value: 1 ether}("ref")` with a low gas price. The transaction enters the mempool.
3. Network congestion delays execution for 12 hours. The oracle rate updates to `1.051e18`.
4. The transaction executes. `viewSwapRsETHAmountAndFee(1 ether)` computes:
   - `fee = 1e18 * feeBps / 10_000`
   - `rsETHAmount = (1e18 - fee) * 1e18 / 1.051e18`
5. Alice receives fewer wrsETH tokens than she would have at the rate she observed. No revert occurs because there is no minimum-output or deadline check. [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-243)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV2.sol (L207-218)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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
