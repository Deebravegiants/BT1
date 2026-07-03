Now I have enough context to write the finding. The pattern is clear across multiple pool contracts: user-facing `deposit()` functions calculate output amounts using a live oracle rate but accept no minimum output parameter, directly analogous to the OtimFee "no maximum gas price" data-validation gap.

---

### Title
Missing Minimum Output Protection in Pool `deposit()` Functions Exposes Users to Unbounded Slippage - (File: contracts/pools/RSETHPoolV2.sol, RSETHPoolV2NBA.sol, RSETHPoolV3.sol, RSETHPoolNoWrapper.sol, RSETHPool.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol, RSETHPoolV2ExternalBridge.sol, agETH/AGETHPoolV3.sol)

### Summary
Every user-facing `deposit()` function across the L2 pool family computes the rsETH/agETH output amount from a live oracle rate at execution time, but accepts no `minAmountOut` parameter. Users have no on-chain protection against receiving fewer tokens than they expected when the oracle rate moves between transaction submission and inclusion.

### Finding Description
The `deposit()` functions in all L2 pool contracts follow the same pattern:

```solidity
// RSETHPoolV2.sol – deposit(string memory referralId)
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The output is computed entirely from the oracle rate at execution time:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [2](#0-1) 

The identical pattern appears in every sibling pool: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

By contrast, the L1 `LRTDepositPool` explicitly requires a caller-supplied minimum:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...
``` [7](#0-6) 

The check is enforced in `_beforeDeposit`:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [8](#0-7) 

No equivalent guard exists in any of the L2 pool `deposit()` functions.

### Impact Explanation
A user who previews the rate off-chain and submits a `deposit()` transaction has no on-chain guarantee about the rsETH/agETH amount they will receive. If the oracle rate increases between submission and execution (rsETH appreciates in ETH terms), the user receives fewer tokens than expected with no recourse. The contract delivers fewer tokens than the user was shown at preview time, satisfying the "contract fails to deliver promised returns, but doesn't lose value" criterion.

**Impact: Low** — the user's deposited ETH/token value is not stolen, but the promised token output is not guaranteed.

### Likelihood Explanation
The rsETH oracle rate increases continuously as staking rewards accrue. Any transaction that sits in the mempool for more than a few blocks during a period of rapid rate appreciation (e.g., a large reward distribution event) will silently deliver fewer tokens than the user previewed. This is a normal, recurring network condition, not an exceptional one. Any unprivileged depositor calling `deposit()` on any of the affected L2 pools is exposed on every transaction.

### Recommendation
Add a `uint256 minRsETHAmountExpected` (or `minAgETHAmountExpected`) parameter to every `deposit()` overload in all affected pool contracts, and revert if the computed output falls below it — mirroring the existing pattern in `LRTDepositPool._beforeDeposit()`.

### Proof of Concept
1. Alice calls `RSETHPoolV2.viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `0.95 wrsETH` at the current oracle rate.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is included, a large staking-reward distribution causes the rsETH oracle rate to increase by 2%.
4. Alice's transaction executes; `viewSwapRsETHAmountAndFee` now returns `≈0.931 wrsETH`.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the lower amount with no revert.
6. Alice receives ~2% fewer tokens than she was shown, with no on-chain protection and no way to prevent it. [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L107-118)
```text
    event SwapOccurred(address indexed user, uint256 rsETHAmount, uint256 fee, string referralId);
    event FeesWithdrawn(uint256 feeEarnedInETH);
    event BridgedETHToL1ViaNativeBridge(address indexed l1Receiver, uint256 ethBalanceMinusFees);
    event FeeBpsSet(uint256 feeBps);
    event OracleSet(address oracle);
    event L1VaultETHForL2ChainSet(address l1VaultETHForL2Chain);
    event L2BridgeSet(address l2Bridge);
    event MessengerSet(address messenger);
    event Paused(address account);
    event Unpaused(address account);
    event DailyMintLimitSet(uint256 dailyMintLimit);

```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
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

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
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

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
