### Title
Missing Minimum Output Slippage Check in `deposit()` Functions Allows Users to Receive Fewer rsETH Than Expected - (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
The `deposit()` functions across all L2 pool contracts compute the rsETH output amount from a live oracle rate at execution time, but accept no `minRsETHAmountExpected` parameter. A user who previews the swap off-chain and submits a transaction may receive materially fewer rsETH than anticipated if the oracle rate moves before the transaction is included, with no on-chain protection to revert.

### Finding Description
`RSETHPoolV2.deposit()`, `RSETHPoolV3.deposit()`, `RSETHPool.deposit()`, and `RSETHPoolNoWrapper.deposit()` all follow the same pattern:

```solidity
// RSETHPoolV2.sol line 207-219
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

`viewSwapRsETHAmountAndFee` divides by the live oracle rate:

```solidity
// RSETHPoolV2.sol line 225-234
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

If `rsETHToETHrate` increases between the user's off-chain simulation and on-chain execution, `rsETHAmount` decreases proportionally. There is no parameter for the user to specify a minimum acceptable output, and no on-chain check that reverts if the computed amount falls below a threshold.

By contrast, the L1 `LRTDepositPool` correctly implements this protection:

```solidity
// LRTDepositPool.sol line 648-670
function _beforeDeposit(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected)
    private view returns (uint256 rsethAmountToMint)
{
    ...
    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    if (rsethAmountToMint < minRSETHAmountExpected) {
        revert MinimumAmountToReceiveNotMet();
    }
}
```

The same gap exists in the token-deposit overloads of `deposit(address token, uint256 amount, string memory referralId)` in `RSETHPoolV3` and `RSETHPool`/`RSETHPoolNoWrapper`, where the token-to-rsETH rate depends on two oracle reads (`rsETHToETHrate` and `tokenToETHRate`), compounding the exposure.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user deposits ETH or an LST and receives fewer rsETH than they simulated. Their deposited ETH is not lost (it is held by the pool and bridged to L1), but the rsETH minted to them is less than the amount they agreed to accept. The shortfall is bounded by how much the oracle rate moves during the mempool delay, which on L2s with short block times is typically small but non-zero and can be larger during periods of rapid rsETH appreciation.

### Likelihood Explanation
**Medium.** The oracle rate (`getRate()`) reflects the rsETH/ETH exchange rate, which increases monotonically as staking rewards accrue. Any deposit that sits in the mempool for more than a few seconds during a rate update is affected. On L2 chains with public mempools (Arbitrum, Optimism, Unichain), the window is short but real. The issue affects every unprivileged depositor on every deployed L2 pool.

### Recommendation
Add a `minRsETHAmountExpected` parameter to each `deposit()` overload and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool._beforeDeposit()`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

Apply the same fix to the token-deposit overloads in `RSETHPoolV3`, `RSETHPool`, and `RSETHPoolNoWrapper`.

### Proof of Concept
1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` wrsETH at the current oracle rate.
2. Alice submits `RSETHPoolV2.deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is included, the rsETH oracle rate ticks upward (e.g., due to a reward accrual update).
4. Alice's transaction executes; `viewSwapRsETHAmountAndFee` now returns `X - delta` because `rsETHToETHrate` is higher.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
6. Alice receives fewer wrsETH than she expected, with no recourse.

The same scenario applies to `RSETHPoolV3.deposit()` (lines 246–265 and 271–293), `RSETHPool.deposit()` (lines 265–278 and 284–305), and `RSETHPoolNoWrapper.deposit()` (lines 231–244 and 250–271). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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
