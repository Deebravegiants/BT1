### Title
Missing Slippage Protection in L2 Pool `deposit()` Functions Exposes Users to Unfavorable Exchange Rates - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
The `deposit()` functions in `RSETHPoolV3` and `RSETHPoolNoWrapper` calculate the wrsETH/rsETH output amount dynamically at execution time using the current oracle rate, but accept no `minRsETHAmount` parameter. Users cannot protect themselves against oracle rate changes that occur between transaction submission and on-chain execution, causing them to receive fewer receipt tokens than expected with no recourse.

### Finding Description
In `RSETHPoolV3`, both ETH and token deposit paths compute the output amount at execution time:

```solidity
// RSETHPoolV3.sol lines 258, 286
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
// ...
wrsETH.mint(msg.sender, rsETHAmount);
```

`viewSwapRsETHAmountAndFee` reads the live oracle rate:

```solidity
// RSETHPoolV3.sol lines 304, 307
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Neither `deposit(string memory referralId)` nor `deposit(address token, uint256 amount, string memory referralId)` accepts a minimum acceptable output amount. The same pattern is present in `RSETHPoolNoWrapper.deposit()`.

This is in direct contrast with the L1 counterpart `LRTDepositPool.depositETH()` and `depositAsset()`, which both accept and enforce a `minRSETHAmountExpected` parameter validated in `_beforeDeposit()`:

```solidity
// LRTDepositPool.sol lines 667-669
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The oracle rate (`getRate()`) is sourced from an external oracle contract and can change between the time a user previews the swap and the time the transaction executes. On L2 chains, this window can be extended by sequencer delays or mempool congestion.

### Impact Explanation
A user who previews the swap off-chain using `viewSwapRsETHAmountAndFee()` and then submits a `deposit()` transaction may receive materially fewer wrsETH/rsETH tokens than expected if the oracle rate increases before their transaction is included. The deposited ETH/tokens remain in the protocol (no direct fund loss), but the user receives fewer receipt tokens than they were shown, meaning their position is worth less than anticipated. This maps to **Low** impact: contract fails to deliver promised returns, but does not lose value.

### Likelihood Explanation
The oracle rate increases monotonically as staking rewards accrue. Any oracle update that occurs between a user's off-chain preview and on-chain execution will silently reduce the user's output. On L2 chains with sequencers, transaction ordering is not guaranteed, making this a realistic scenario for any active depositor. No privileged action is required to trigger the condition.

### Recommendation
Add a `minRsETHAmount` parameter to all `deposit()` overloads in `RSETHPoolV3` and `RSETHPoolNoWrapper`, and revert if the computed output falls below it, mirroring the existing protection in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount) external payable {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert SlippageExceeded();
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `X` wrsETH.
2. Before the user's `deposit()` transaction is included, the oracle rate increases (e.g., due to a reward accrual update).
3. User's `deposit()` executes; `viewSwapRsETHAmountAndFee` now returns `X - delta` wrsETH because `rsETHToETHrate` is higher.
4. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
5. User receives fewer wrsETH than previewed, with no ability to have prevented this outcome.

The L1 pool `LRTDepositPool` avoids this by enforcing `minRSETHAmountExpected` in `_beforeDeposit()` at lines 667–669. The L2 pools have no equivalent guard. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L250-271)
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

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
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
