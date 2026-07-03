### Title
Missing Minimum rsETH Output Check in `deposit()` Allows Oracle-Rate Slippage to Silently Harm Depositors - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
All L2 pool `deposit()` functions (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) compute the rsETH/wrsETH output amount at execution time using a live oracle rate, but accept no `minRSETHAmountExpected` parameter. A depositor has no way to bound the minimum output they will receive, so any oracle rate update that occurs between transaction submission and inclusion silently reduces the tokens minted to the user.

### Finding Description
Every L2 pool `deposit()` function follows the same pattern:

```solidity
// RSETHPoolV3.sol – ETH deposit (lines 246-265)
function deposit(string memory referralId) external payable ... {
    uint256 amount = msg.value;
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum check
}
```

`viewSwapRsETHAmountAndFee` divides by the live oracle rate at execution time:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // RSETHPoolV3.sol:307
```

The oracle rate (`rsETHOracle.getRate()`) is a cross-chain rate that is periodically updated by the protocol. Because rsETH accrues staking rewards, the rate is expected to increase over time. Any rate update that lands in the same block as, or just before, a user's deposit transaction will reduce `rsETHAmount` below what the user observed off-chain when constructing the transaction.

By contrast, the mainnet `LRTDepositPool.depositETH()` and `depositAsset()` both accept a `minRSETHAmountExpected` parameter and enforce it inside `_beforeDeposit`:

```solidity
// LRTDepositPool.sol:667-669
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

No equivalent guard exists in any of the L2 pool `deposit()` functions.

The same gap is present in:
- `RSETHPoolV3ExternalBridge.deposit()` (lines 366-384, 390-412)
- `RSETHPoolV3WithNativeChainBridge.deposit()` (lines 282-301, 307-329)
- `RSETHPoolNoWrapper.deposit()` (lines 231-244, 250-271)

### Impact Explanation
**Low.** A depositor receives fewer wrsETH/rsETH tokens than they observed when simulating the transaction. Their ETH/LST is fully consumed; they are not made whole. The protocol does not lose funds, but the user receives less than the promised return. This maps to: *"Contract fails to deliver promised returns, but doesn't lose value."*

### Likelihood Explanation
**Medium.** The rsETH oracle rate is updated regularly by the protocol's cross-chain rate broadcasting infrastructure. On any L2 with non-trivial mempool latency or block time, a rate update and a user deposit can land in the same block. No special attacker action is required — the loss occurs passively whenever the oracle updates between a user's `eth_call` simulation and the transaction's inclusion.

### Recommendation
Add a `minRSETHAmountExpected` parameter to all L2 pool `deposit()` overloads and revert if the computed output falls below it, mirroring the guard already present in `LRTDepositPool._beforeDeposit`. For example:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused ...
{
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(msg.value);
    if (rsETHAmount < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    ...
}
```

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes `rsETHAmount = X`.
2. User submits `deposit{value: 1 ether}(referralId)` targeting `RSETHPoolV3`.
3. Before the transaction is included, the protocol's rate broadcaster updates `rsETHOracle` to a higher rate (rsETH appreciated).
4. `deposit()` executes: `viewSwapRsETHAmountAndFee` now returns `rsETHAmount = X - delta` (fewer tokens because the denominator `rsETHToETHrate` is larger).
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
6. User receives `X - delta` wrsETH instead of `X`, with no recourse. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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
