### Title
Missing Minimum rsETH Output Amount in L2 Pool `deposit()` Functions — (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol)

---

### Summary

All L2 pool `deposit()` functions accept ETH or LST tokens from users and compute the rsETH/wrsETH output based on the current oracle rate, but expose no `minRsETHAmount` parameter for users to specify a minimum acceptable output. If the oracle rate changes between transaction submission and execution, users receive fewer rsETH than expected with no recourse. The L1 `LRTDepositPool` already enforces this protection via `minRSETHAmountExpected`, but the L2 pool contracts do not.

---

### Finding Description

Every L2 pool `deposit()` function computes the rsETH output by calling `viewSwapRsETHAmountAndFee()`, which reads the live rate from `rsETHOracle` at execution time:

**RSETHPool.sol** — ETH deposit:
```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
}
``` [1](#0-0) 

**RSETHPoolV3.sol** — ETH deposit:
```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER) {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}
``` [2](#0-1) 

**RSETHPoolV3ExternalBridge.sol** — ETH deposit: [3](#0-2) 

**RSETHPoolNoWrapper.sol** — ETH deposit: [4](#0-3) 

**RSETHPoolV2ExternalBridge.sol** — ETH deposit: [5](#0-4) 

The rate computation in all pools reads the live oracle at execution time:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [6](#0-5) 

The same pattern applies to token deposits in `RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolNoWrapper`: [7](#0-6) [8](#0-7) 

By contrast, the L1 `LRTDepositPool` already enforces a user-supplied minimum:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...
function depositAsset(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected, ...) external ...
``` [9](#0-8) 

The slippage check is enforced in `_beforeDeposit`:
```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [10](#0-9) 

No equivalent guard exists in any L2 pool `deposit()` function.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who previews the expected rsETH output off-chain (or via `viewSwapRsETHAmountAndFee`) and then submits a `deposit()` transaction has no on-chain guarantee that the rate will be the same at execution time. If the `rsETHOracle` is updated between submission and execution (e.g., a Chainlink keeper pushes a new rate), the user receives fewer rsETH than expected with no ability to revert. The deposited ETH/LST is consumed and the shortfall is unrecoverable. The user does not lose their principal in ETH terms, but receives a worse rsETH-per-ETH ratio than they agreed to.

---

### Likelihood Explanation

**Medium.** The `rsETHOracle` on each L2 is a live rate feed (Chainlink or equivalent) that is updated periodically — typically when the rate moves beyond a deviation threshold or on a heartbeat schedule. On chains with slower sequencer throughput or during periods of high mempool congestion, a user's transaction can sit pending long enough for an oracle update to occur. The token-deposit variant is additionally exposed to the token-to-ETH oracle (`supportedTokenOracle[token]`), which is a second independent rate that can shift: [11](#0-10) 

---

### Recommendation

Add a `minRsETHAmount` parameter to every public `deposit()` overload in all L2 pool contracts. After computing `rsETHAmount`, revert if it falls below the caller's stated minimum:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
    ...
}
```

This mirrors the protection already present in `LRTDepositPool.depositETH` and `LRTDepositPool.depositAsset` on L1, and matches the fix applied in the referenced Portfolio.sol PR 307.

---

### Proof of Concept

1. rsETH oracle rate on the L2 is 1.05 ETH/rsETH. User calls `deposit{value: 1 ether}("ref")` on `RSETHPoolV3`, expecting ≈ 0.952 wrsETH (after fee).
2. Before the transaction is included, the Chainlink keeper pushes a new rate: 1.10 ETH/rsETH.
3. The transaction executes. `viewSwapRsETHAmountAndFee(1 ether)` now returns ≈ 0.909 wrsETH.
4. The user receives ≈ 0.909 wrsETH — a shortfall of ≈ 0.043 wrsETH (~4.5%) with no revert and no recourse.
5. The same scenario applies to token deposits where both `rsETHToETHrate` and `tokenToETHRate` can shift independently between submission and execution. [6](#0-5) [11](#0-10)

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

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
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

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
