### Title
L2 Pool `deposit()` Functions Lack Slippage Protection - (File: `contracts/pools/RSETHPoolV3.sol`)

### Summary
All L2 pool `deposit()` functions mint `wrsETH` (or transfer `rsETH`) to users based solely on the current oracle rate, with no caller-supplied minimum output amount parameter. Unlike the L1 `LRTDepositPool`, which enforces a `minRSETHAmountExpected` check, the L2 pools provide zero slippage protection to depositors.

### Finding Description
The `deposit()` functions in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolNoWrapper`, and `RSETHPool` compute the output amount entirely from the live oracle rate and immediately mint/transfer tokens to the caller, with no floor on the amount received:

```solidity
// RSETHPoolV3.sol lines 246-265
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum check
    ...
}
```

The rate is fetched from `rsETHOracle` at execution time:

```solidity
// RSETHPoolV3.sol lines 299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

By contrast, the L1 `LRTDepositPool._beforeDeposit()` explicitly enforces a caller-supplied minimum:

```solidity
// LRTDepositPool.sol lines 665-669
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The same missing-minimum pattern is present in:
- `RSETHPoolV3.deposit(address token, uint256 amount, string)` (line 271)
- `RSETHPoolV3ExternalBridge.deposit()` (analogous structure)
- `RSETHPoolNoWrapper.deposit()` (lines 231, 250)
- `RSETHPool.deposit()` (analogous structure)

### Impact Explanation
A user who submits a deposit transaction cannot guarantee the minimum `wrsETH` they will receive. If the oracle rate is updated (legitimately or via a cross-chain message) in the same block or between the user's signature and on-chain execution, the user receives fewer `wrsETH` than they observed off-chain. The user's ETH/LST is fully consumed; they simply receive less output than expected with no recourse. This matches the allowed impact: **Low — contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The `rsETHOracle` rate is updated periodically via cross-chain rate propagation or manual manager calls. Any deposit transaction that lands in the same block as a rate update, or that is delayed in the mempool across a rate update, silently delivers a worse-than-expected output. No attacker capability is required; ordinary network conditions are sufficient.

### Recommendation
Add a `minRSETHAmountExpected` parameter to every public `deposit()` overload in all L2 pool contracts, mirroring the L1 pattern:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` wrsETH at the current rate.
2. Alice submits `deposit{value: 1 ether}("ref")` to `RSETHPoolV3`.
3. Before Alice's transaction is mined, the oracle rate is updated (e.g., rsETH appreciates), increasing `rsETHToETHrate`.
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / newHigherRate` → Alice receives `X' < X` wrsETH.
5. Alice has no on-chain mechanism to reject this outcome; the contract accepted her ETH and minted fewer tokens than she expected. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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
