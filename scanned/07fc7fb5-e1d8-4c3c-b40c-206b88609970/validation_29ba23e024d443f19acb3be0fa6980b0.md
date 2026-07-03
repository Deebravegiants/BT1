### Title
Missing Minimum Output Validation in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
The L2 pool contracts (`RSETHPool`, `RSETHPoolV3`, `RSETHPoolNoWrapper`) expose public `deposit()` functions that swap ETH or supported tokens for rsETH/wrsETH using a live oracle rate, but provide no `minOut` (minimum rsETH output) parameter. Because the rsETH/ETH rate is fetched at execution time and can increase between transaction submission and inclusion, users have no on-chain mechanism to enforce a minimum acceptable output.

### Finding Description
Every L2 pool contract exposes two public deposit entry points — one for native ETH and one for ERC-20 tokens — that compute the rsETH output by reading the current oracle rate at execution time:

**`RSETHPool.deposit(string referralId)`** (ETH path): [1](#0-0) 

**`RSETHPool.deposit(address token, uint256 amount, string referralId)`** (token path): [2](#0-1) 

The rsETH amount is computed via `viewSwapRsETHAmountAndFee`, which divides the post-fee input by the live oracle rate: [3](#0-2) 

The identical pattern exists in `RSETHPoolV3`: [4](#0-3) [5](#0-4) 

And in `RSETHPoolNoWrapper`: [6](#0-5) [7](#0-6) 

None of these functions accept or enforce a caller-supplied minimum rsETH output. The oracle rate used is the live `rsETHOracle.getRate()` value at the moment of execution.

Contrast this with the L1 `LRTDepositPool`, which correctly accepts a `minRSETHAmountExpected` parameter and enforces it before minting: [8](#0-7) 

The L1 oracle `updateRSETHPrice()` is a **public, permissionless** function — any address can call it to push the latest on-chain rate: [9](#0-8) 

The rsETH price is monotonically non-decreasing in normal operation (rewards accrue, TVL grows). When the oracle rate increases between a user's transaction submission and its inclusion, the user receives fewer rsETH tokens than they observed off-chain, with no recourse.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

Users deposit ETH or LSTs and receive fewer rsETH tokens than the rate they observed when constructing the transaction. Their principal (ETH/LST) is not lost — it is held by the pool — but the rsETH output is silently worse than expected. There is no on-chain protection the user can set to reject an unfavorable execution. This is the direct analog of the HODL `_buyHodl()` missing `minOut` issue: the price can only increase, and users cannot cap the price they are willing to pay.

### Likelihood Explanation
The rsETH/ETH rate is updated on every oracle refresh cycle. On active L2 chains (Arbitrum, Unichain) with moderate block times and mempool congestion, a pending deposit transaction can easily span one or more oracle update events. The L1 `updateRSETHPrice()` is permissionless, so any actor can trigger a rate update immediately before a user's deposit lands. This is a realistic, low-effort condition that requires no privileged access.

### Recommendation
Add a `minRSETHAmountExpected` parameter to all public `deposit()` overloads in `RSETHPool`, `RSETHPoolV3`, and `RSETHPoolNoWrapper`, mirroring the existing pattern in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert InsufficientOutput();
    ...
}
```

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes `rsETHAmount = X`.
2. User submits `RSETHPool.deposit{value: 1 ether}("ref")` — no `minOut` is possible.
3. Before the transaction is included, anyone calls `LRTOracle.updateRSETHPrice()` (permissionless), pushing the rsETH/ETH rate higher.
4. The L2 oracle is updated to reflect the new rate (via the cross-chain rate propagation path).
5. The user's transaction executes: `viewSwapRsETHAmountAndFee` now returns `rsETHAmount = X - delta` (fewer rsETH due to higher rate).
6. The user receives fewer rsETH than `X` with no on-chain protection and no revert.

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```
