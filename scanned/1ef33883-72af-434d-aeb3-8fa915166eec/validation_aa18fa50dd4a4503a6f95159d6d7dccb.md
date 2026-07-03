### Title
Missing Minimum Output Slippage Guard in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
All L2 RSETHPool deposit entry points (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV3`, `RSETHPoolNoWrapper`) accept ETH or ERC-20 tokens from unprivileged users and compute the rsETH output solely from the live oracle rate at execution time. None of these functions expose a `minRsETHAmountExpected` parameter. If the oracle rate is updated between transaction submission and execution, users silently receive fewer rsETH than they anticipated and cannot revert.

### Finding Description
The rsETH output in every L2 pool is computed by `viewSwapRsETHAmountAndFee`, which divides the fee-adjusted input by the current `rsETHToETHrate` returned by the oracle:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

A higher `rsETHToETHrate` (rsETH appreciating) yields fewer rsETH for the same ETH input. Because the oracle rate is updated by the protocol via cross-chain messaging and can change at any block, a user who submits a deposit transaction at rate R may have it execute at rate R′ > R, receiving materially fewer rsETH with no on-chain protection.

The L1 `LRTDepositPool` demonstrates the protocol's own awareness of this risk: both `depositETH` and `depositAsset` accept a `minRSETHAmountExpected` argument and revert in `_beforeDeposit` if the computed mint falls below it. [1](#0-0) [2](#0-1) 

The L2 pool variants omit this guard entirely. For example, `RSETHPoolV3.deposit` (ETH path): [3](#0-2) 

And the token path: [4](#0-3) 

The same pattern is present in `RSETHPool.deposit`: [5](#0-4) 

`RSETHPoolNoWrapper.deposit`: [6](#0-5) 

`RSETHPoolV2.deposit`: [7](#0-6) 

`RSETHPoolV2NBA.deposit`: [8](#0-7) 

The rate computation shared by all of them: [9](#0-8) 

### Impact Explanation
**Low — Contract fails to deliver promised returns, but does not lose value.**

A user who previews the deposit off-chain (or via `viewSwapRsETHAmountAndFee`) and then submits the transaction may receive fewer rsETH than expected if the oracle rate is updated before their transaction is included. The shortfall is not extracted by an attacker; it remains in the pool as a higher ETH-per-rsETH backing. The user suffers a silent reduction in rsETH received with no recourse, because the transaction cannot revert on their behalf.

### Likelihood Explanation
**Low-Medium.** The rsETH oracle rate is updated by the protocol via cross-chain messaging on a regular cadence. On L2 networks, user transactions can sit in the mempool or be sequenced after a rate update. No privileged attacker action is required — a routine protocol rate update landing before a user's deposit is sufficient to trigger the shortfall. The L1 deposit pool's own `minRSETHAmountExpected` guard confirms the protocol considers this a real risk in the deposit flow.

### Recommendation
Add a `minRsETHAmountExpected` parameter to every `deposit()` overload in all L2 pool contracts. After computing `rsETHAmount` via `viewSwapRsETHAmountAndFee`, revert if `rsETHAmount < minRsETHAmountExpected`. This mirrors the protection already present in `LRTDepositPool._beforeDeposit`. [10](#0-9) 

### Proof of Concept
1. The current oracle rate is `1.05e18` (1 rsETH = 1.05 ETH). User calls `RSETHPoolV3.deposit{value: 1 ether}("ref")` expecting `≈ 0.952 rsETH` (after fee).
2. Before the transaction is included, the protocol's cross-chain rate propagation updates the oracle to `1.10e18`.
3. The user's transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 rsETH` — roughly 4.5% less than expected.
4. No revert occurs; the user receives `0.909 rsETH` with no ability to reject the worse rate. [9](#0-8)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```
