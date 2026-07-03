### Title
Missing Minimum Output Amount (Slippage Protection) in L2 Pool Deposit Functions — (File: contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
All L2 pool `deposit` functions accept user ETH or tokens and mint/transfer rsETH based solely on the oracle rate at execution time, with no on-chain mechanism for the depositor to specify a minimum acceptable rsETH output. The L1 counterpart (`LRTDepositPool.depositETH`) enforces a `minRSETHAmountExpected` check, but this protection is absent across every L2 pool variant.

### Finding Description
The `deposit(string memory referralId)` and `deposit(address token, uint256 amount, string memory referralId)` functions in `RSETHPoolNoWrapper`, `RSETHPool`, `RSETHPoolV3`, and `RSETHPoolV3ExternalBridge` compute the rsETH output entirely from the oracle rate at the moment of execution:

```solidity
// RSETHPoolNoWrapper.sol L231-243
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    rsETH.safeTransfer(msg.sender, rsETHAmount);   // no floor check
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

`viewSwapRsETHAmountAndFee` divides by `getRate()` (the live oracle value) with no user-supplied lower bound:

```solidity
// RSETHPoolNoWrapper.sol L277-286
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

The L1 `LRTDepositPool` explicitly guards against this with a `minRSETHAmountExpected` parameter enforced inside `_beforeDeposit`:

```solidity
// LRTDepositPool.sol L76-93
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) external payable ...
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
```

```solidity
// LRTDepositPool.sol L666-669
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The same gap exists in `RSETHPool.deposit`, `RSETHPoolV3.deposit`, and `RSETHPoolV3ExternalBridge.deposit`.

### Impact Explanation
A depositor submits a transaction expecting X rsETH at the current oracle rate. If the oracle rate rises (rsETH becomes more expensive in ETH terms) before the transaction is included — due to normal rate accrual, block reordering, or congestion — the user receives fewer rsETH tokens than anticipated. Because rsETH represents a proportional claim on the underlying restaked assets, receiving fewer tokens means the user's on-chain claim is permanently smaller than the value they deposited. The ETH remains in the pool and is eventually bridged to L1, but the rsETH shortfall is not corrected retroactively.

**Impact class:** Low — Contract fails to deliver promised returns, but doesn't lose value.

### Likelihood Explanation
rsETH accrues value continuously as EigenLayer rewards accumulate, so the oracle rate (`getRate()`) increases over time. Any deposit that sits in the mempool for more than a few blocks is exposed to a rate drift. On congested L2s (Arbitrum, Optimism, Unichain), transactions can be delayed by minutes, making the rate-at-submission vs. rate-at-execution gap material. No adversarial action is required; ordinary network conditions are sufficient.

### Recommendation
Add a `minRSETHAmountExpected` parameter to every L2 pool `deposit` function and revert if the computed output falls below it, mirroring the L1 `LRTDepositPool` pattern:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

Apply the same pattern to the token-deposit overload and to all pool variants (`RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`).

### Proof of Concept
1. Oracle reports `getRate() = 1.05e18` (1 rsETH = 1.05 ETH). User submits `deposit{value: 1 ether}()` expecting ≈ 0.952 rsETH (after fee).
2. Before the transaction is mined, the oracle updates to `1.06e18` due to reward accrual.
3. Transaction executes: `rsETHAmount = (1e18 - fee) * 1e18 / 1.06e18 ≈ 0.943 rsETH`.
4. User receives ~0.009 rsETH less than expected with no on-chain recourse. The shortfall is permanent — the pool does not compensate the difference.

The root cause is confirmed at: [1](#0-0) [2](#0-1) 

Contrast with the protected L1 path: [3](#0-2) [4](#0-3) 

The same unprotected pattern is present in all other L2 pool variants: [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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
