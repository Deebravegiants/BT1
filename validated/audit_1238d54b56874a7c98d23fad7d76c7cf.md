### Title
Missing Slippage Protection in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPool.sol, RSETHPoolV2.sol, RSETHPoolV3.sol, RSETHPoolV2NBA.sol, RSETHPoolV2ExternalBridge.sol, RSETHPoolV3ExternalBridge.sol, RSETHPoolV3WithNativeChainBridge.sol, RSETHPoolNoWrapper.sol)

---

### Summary

All L2 pool `deposit()` functions compute the rsETH output amount at runtime using the current oracle rate and provide no `minRsETHAmountExpected` guard. Users cannot specify a minimum acceptable output, leaving them exposed to receiving fewer rsETH than anticipated whenever the oracle rate moves between transaction submission and execution.

---

### Finding Description

The L1 `LRTDepositPool` correctly enforces slippage protection:

```solidity
// LRTDepositPool.sol
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...
function depositAsset(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected, ...) external ...
``` [1](#0-0) [2](#0-1) 

The slippage check is enforced inside `_beforeDeposit`:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [3](#0-2) 

Every L2 pool contract's `deposit()` function is missing this parameter entirely. The rsETH amount is computed at runtime from the oracle rate and immediately minted/transferred with no floor check:

```solidity
// RSETHPool.sol – ETH deposit
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount); // runtime rate
    feeEarnedInETH += fee;
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount); // no floor check
    ...
}
``` [4](#0-3) 

The same pattern is present in every pool variant: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

The rate used in every case is fetched live from the oracle:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate(); // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [10](#0-9) 

This is structurally identical to the reported bug: the "expected output" is computed at execution time with no user-supplied floor, so the user has zero protection against an unfavorable rate at the moment of execution.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who observes a favorable rsETH/ETH rate off-chain and submits a `deposit()` transaction has no on-chain guarantee they will receive at least that amount. If the oracle rate is updated (legitimately or otherwise) between submission and inclusion, the user silently receives fewer rsETH than expected with no revert. Because rsETH represents a proportional claim on protocol assets, receiving fewer rsETH for the same ETH input is a direct reduction in the user's share of the protocol.

---

### Likelihood Explanation

**Low.** The rsETH oracle rate is not an AMM spot price; it reflects the protocol's aggregate TVL divided by total rsETH supply and changes slowly. An unprivileged attacker cannot trivially manipulate it in a single block the way a Curve pool can be sandwiched. However, the risk is real in two realistic scenarios:

1. A pending transaction sits in the mempool across an oracle rate update (e.g., a cross-chain rate message is relayed).
2. A user deposits a large amount on a chain where the oracle is the `InterimRSETHOracle` (manually set), and the rate is updated while their transaction is pending.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to every `deposit()` overload in all L2 pool contracts, mirroring the L1 `LRTDepositPool` pattern:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` rsETH at the current oracle rate.
2. Alice submits `RSETHPool.deposit("ref")` with `1 ether`.
3. Before Alice's transaction is mined, the oracle rate is updated (e.g., a cross-chain rate message is relayed, increasing the rsETH/ETH rate).
4. Alice's transaction executes at the new, higher rate, and she receives `X - Y` rsETH (fewer than expected) with no revert.
5. Alice has no recourse; the contract accepted her ETH and minted fewer rsETH than she anticipated, with no slippage floor to protect her. [4](#0-3) [11](#0-10)

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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
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

**File:** contracts/LRTDepositPool.sol (L648-669)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-301)
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
