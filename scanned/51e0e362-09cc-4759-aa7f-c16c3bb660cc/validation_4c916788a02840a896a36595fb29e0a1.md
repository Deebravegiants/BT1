### Title
No User-Controlled Minimum Output on Deposit Allows Admin Fee Increase to Silently Reduce Received rsETH - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
The `deposit()` functions across the L2 pool contracts accept no `minAmountOut` (or equivalent) parameter. The admin can call `setFeeBps()` at any time — including between a user's off-chain simulation and on-chain execution — causing the user to receive fewer wrsETH/rsETH tokens than anticipated, with no on-chain protection.

### Finding Description
In `RSETHPoolV3ExternalBridge.sol`, `setFeeBps()` is callable by `DEFAULT_ADMIN_ROLE` with no timelock and allows `feeBps` to be set anywhere from 0 to 10,000 (0–100%):

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol L744-748
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
``` [1](#0-0) 

The ETH `deposit()` function applies the current `feeBps` at execution time and mints `wrsETH` based on the post-fee amount, but accepts no minimum output guard:

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol L366-384
function deposit(string memory referralId) external payable ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    ...
}
``` [2](#0-1) 

The fee is computed as:

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol L419
fee = amount * feeBps / 10_000;
``` [3](#0-2) 

The same pattern exists in `RSETHPoolV3.sol` (fee capped at 10%, `DEFAULT_ADMIN_ROLE`, no timelock) and `RSETHPoolNoWrapper.sol` (fee up to 100%, `TIMELOCK_ROLE`): [4](#0-3) [5](#0-4) 

### Impact Explanation
A user calls `viewSwapRsETHAmountAndFee()` off-chain to preview their expected wrsETH output, then submits `deposit()`. If the admin updates `feeBps` (even without malicious intent — e.g., a routine fee adjustment) before the user's transaction is mined, the user receives fewer wrsETH tokens than the amount they simulated, with no on-chain recourse. In `RSETHPoolV3ExternalBridge.sol`, the fee can be raised to 100%, meaning the user could receive 0 wrsETH for their deposited ETH. The contract fails to deliver the promised return the user observed at simulation time.

**Impact:** Low — Contract fails to deliver promised returns, but doesn't lose value (fees accrue to the protocol).

### Likelihood Explanation
The admin can update `feeBps` in a single transaction with no delay. Any routine fee increase — even a well-intentioned one — can silently affect pending user transactions. On L2 networks with fast block times and public mempools, the window for this to occur is small but non-zero. The likelihood is low-to-medium for unintentional impact and higher if the admin acts opportunistically.

### Recommendation
Add a `minAmountOut` parameter to both `deposit()` overloads across all pool variants, and revert if the computed `rsETHAmount` falls below it:

```solidity
function deposit(string memory referralId, uint256 minAmountOut) external payable ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minAmountOut) revert SlippageExceeded();
    ...
}
```

Alternatively, implement a time-delayed fee update mechanism (e.g., a two-step commit/apply with a minimum notice period) so users can observe pending fee changes before they take effect.

### Proof of Concept
1. Current `feeBps` = 10 (0.1%). User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive ~`X` wrsETH.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the user's transaction is mined, admin calls `setFeeBps(500)` (5%), raising the fee.
4. User's transaction executes with `feeBps = 500`. They receive ~`X * 0.95` wrsETH — 5% less than expected — with no revert or warning.
5. In the extreme case (`feeBps = 10_000`), the user receives 0 wrsETH for 1 ETH deposited. [2](#0-1) [1](#0-0)

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L744-748)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-522)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L524-530)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(TIMELOCK_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();

        feeBps = _feeBps;

        emit FeeBpsSet(_feeBps);
    }
```
