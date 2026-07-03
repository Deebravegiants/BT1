### Title
No User-Controlled Slippage Protection in L2 Pool `deposit` Functions - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

All L2 pool `deposit` functions compute the rsETH/wrsETH output amount by calling `viewSwapRsETHAmountAndFee` (a view/preview function) on-chain and immediately use the result without any user-supplied minimum-amount guard. This is the direct analog of the Illuminate `yield` bug: a preview value is consumed on-chain with no validation, making slippage protection non-existent for depositors.

---

### Finding Description

The L1 deposit path (`LRTDepositPool.depositETH` / `depositAsset`) correctly accepts a `minRSETHAmountExpected` parameter and reverts if the computed mint amount falls below it: [1](#0-0) 

Every L2 pool `deposit` function omits this guard entirely. The pattern is identical across all pool variants:

```solidity
// RSETHPool.sol – ETH deposit
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);  // preview on-chain
    feeEarnedInETH += fee;
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);           // no minAmount check
    ...
}
``` [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

`viewSwapRsETHAmountAndFee` derives the output amount from the live oracle rate:

```solidity
uint256 rsETHToETHrate = getRate();          // reads oracle at execution time
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [6](#0-5) 

Because the oracle rate can be updated by the protocol between the moment a user previews the transaction off-chain and the moment the transaction is mined, the user has no on-chain mechanism to enforce a minimum acceptable output. The `viewSwapRsETHAmountAndFee` call is the on-chain equivalent of `sellBasePreview` in the Illuminate bug: it is a preview function whose result is used directly with zero validation.

---

### Impact Explanation

**Low – Contract fails to deliver promised returns, but doesn't lose value.**

A user who previews the deposit off-chain and observes `X` wrsETH may receive materially fewer tokens if the oracle rate is updated (rsETH appreciates in ETH terms) before the transaction is included. The ETH value is not lost from the protocol, but the user receives fewer shares than the rate they observed, with no recourse. This is a systematic, silent shortfall that affects every depositor on every L2 pool variant.

---

### Likelihood Explanation

The rsETH oracle rate is updated regularly as EigenLayer rewards accrue and LST prices move. On L2 chains with slower block times or during periods of high network congestion, the window between a user's off-chain preview and on-chain execution can be several seconds to minutes. Any oracle update in that window silently reduces the user's output. No privileged access or special conditions are required; any ordinary depositor is affected on every deposit.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to all `deposit` overloads in every L2 pool contract, mirroring the existing guard in `LRTDepositPool._beforeDeposit`:

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

This applies to `RSETHPool`, `RSETHPoolV3`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, and any other pool variant that follows the same pattern.

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes `rsETHAmount = 0.95 wrsETH` at oracle rate `R`.
2. Before the user's transaction is mined, the protocol updates the oracle rate to `R' > R` (rsETH has appreciated).
3. User's `deposit{value: 1 ether}(referralId)` executes; `viewSwapRsETHAmountAndFee` is called on-chain at rate `R'`, returning `rsETHAmount' < 0.95 wrsETH`.
4. The contract transfers `rsETHAmount'` to the user with no revert, silently delivering fewer tokens than the user expected.
5. The user has no parameter to set a floor and no way to prevent this outcome. [2](#0-1) [7](#0-6)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L246-293)
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

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-270)
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

    /// @dev Swaps token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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
```
