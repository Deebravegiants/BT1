### Title
Missing Minimum Output Protection in L2 Pool Deposit Functions - (`contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`)

---

### Summary

The L2 pool deposit functions (`deposit()`) across all L2 pool variants lack a `minRsETHAmount` parameter, meaning depositors have no on-chain protection against receiving fewer rsETH tokens than expected. This is in direct contrast to the L1 `LRTDepositPool.depositETH()` and `depositAsset()`, which explicitly enforce a `minRSETHAmountExpected` check. A user who simulates the swap off-chain and submits a transaction can receive materially fewer rsETH tokens if the oracle rate moves between simulation and execution.

---

### Finding Description

The L1 deposit path enforces a minimum output check:

```solidity
// LRTDepositPool.sol
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable ...
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    ...
}
```

Inside `_beforeDeposit`, the check is explicit:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [1](#0-0) 

By contrast, every L2 pool `deposit()` function accepts only the `referralId` (and optionally a token address and amount), with no minimum output parameter:

```solidity
// RSETHPool.sol
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [2](#0-1) 

The same pattern is present in `RSETHPoolV3.deposit()`: [3](#0-2) 

In `RSETHPoolNoWrapper.deposit()`: [4](#0-3) 

And in `RSETHPoolV3ExternalBridge.deposit()`: [5](#0-4) 

The rsETH amount is computed from the oracle rate at execution time:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [6](#0-5) 

If `getRate()` returns a higher value at execution time than at simulation time (i.e., rsETH has appreciated), the depositor receives fewer rsETH tokens than anticipated, with no recourse.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A depositor who simulates the transaction and expects `X` rsETH tokens may receive `X - delta` rsETH tokens if the oracle rate increases between simulation and on-chain execution. Because each rsETH token represents a proportional claim on the underlying restaked ETH, the depositor's total ETH-denominated value is approximately preserved, but the token count shortfall means the contract does not deliver the output the user was promised at simulation time. This is the same vulnerability class as the referenced report: a user-facing swap function with no minimum output guard.

---

### Likelihood Explanation

The rsETH oracle rate (`getRate()`) reflects the accrual of restaking rewards and changes slowly under normal conditions. However, the rate can shift between blocks, and in periods of high network activity or oracle updates, the difference between simulated and executed output can be non-trivial. The risk is amplified for large deposits. The L1 contract's explicit inclusion of `minRSETHAmountExpected` demonstrates the protocol's own awareness that this protection is necessary.

---

### Recommendation

Add a `minRsETHAmount` parameter to all L2 pool `deposit()` functions (ETH and token variants) across `RSETHPool`, `RSETHPoolV3`, `RSETHPoolNoWrapper`, and `RSETHPoolV3ExternalBridge`. After computing `rsETHAmount`, revert if it is below the caller-specified minimum:

```solidity
function deposit(uint256 minRsETHAmount, string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
    ...
}
```

This mirrors the protection already present in `LRTDepositPool._beforeDeposit()`.

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `0.952 rsETH` (oracle rate = 1.05 ETH/rsETH).
2. Alice submits `deposit{value: 1 ether}("ref")` to `RSETHPool`.
3. Before Alice's transaction is mined, the oracle rate updates to 1.10 ETH/rsETH (e.g., due to a reward accrual event).
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 = 0.909e18`.
5. Alice receives `0.909 rsETH` instead of the `0.952 rsETH` she expected — a ~4.5% shortfall in token count — with no revert and no recourse.
6. Had the same deposit been made on L1 via `LRTDepositPool.depositETH(0.952e18, "ref")`, the transaction would have reverted with `MinimumAmountToReceiveNotMet`. [7](#0-6) [2](#0-1)

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
