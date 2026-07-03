### Title
Lack of Slippage Protection in L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV2NBA.sol)

### Summary
All L2 pool `deposit()` functions accept ETH or supported tokens and mint rsETH/wrsETH to the caller, but provide no `minRsETHAmountExpected` guard. The minted amount is computed at execution time using a live oracle rate (`rsETHOracle.getRate()`) and a mutable `feeBps`. Both can change between when a user previews the swap and when the transaction is mined, causing the user to receive fewer tokens than expected with no on-chain recourse.

### Finding Description

Every L2 pool `deposit()` function computes the output amount at execution time:

```solidity
// RSETHPoolV2NBA.sol – deposit()
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

`viewSwapRsETHAmountAndFee` divides by the live oracle rate:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [2](#0-1) 

`feeBps` is mutable by `DEFAULT_ADMIN_ROLE` with no timelock:

```solidity
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
``` [3](#0-2) 

The same pattern is present across every L2 pool variant — `RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper` — none of which accept a `minRsETHAmountExpected` argument.


By contrast, the L1 `LRTDepositPool.depositETH()` explicitly enforces a caller-supplied minimum:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...
``` [4](#0-3) 

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [5](#0-4) 

### Impact Explanation

**Impact: Low** — Contract fails to deliver the promised return without losing the depositor's underlying value.

A user who previews the swap via `viewSwapRsETHAmountAndFee` and then submits a `deposit()` transaction can receive materially fewer wrsETH tokens than quoted if:

1. The oracle rate rises between preview and execution (rsETH appreciates → fewer tokens minted per ETH).
2. `feeBps` is raised before the transaction is mined (more ETH is taken as fee → fewer tokens minted).

In scenario (1) the user's economic value is preserved (fewer but more-valuable tokens). In scenario (2) the user pays a larger fee than expected, which is a direct value loss to the fee collector. In both cases the user has no on-chain mechanism to reject the execution.

### Likelihood Explanation

**Likelihood: Medium** — Oracle rate fluctuations are a continuous, natural market phenomenon on every block. Fee updates require admin action but carry no timelock in `RSETHPoolV2NBA`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPool`, meaning they can take effect in the same block as a pending user deposit.

### Recommendation

Add a `minRsETHAmountExpected` parameter to every `deposit()` overload in all L2 pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV2NBA` and sees they will receive `X` wrsETH.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction is mined, the oracle rate increases (rsETH appreciates) or admin calls `setFeeBps(newHigherFee)`.
4. Transaction executes: `viewSwapRsETHAmountAndFee` now returns `X - delta` wrsETH.
5. User receives `X - delta` wrsETH with no ability to revert — the contract accepted the deposit silently at the worse rate.

### Citations

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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-133)
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L163-167)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
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
