### Title
No Minimum Output Slippage Protection on L2 Pool Deposit Functions - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPool.sol`)

---

### Summary

The L2 pool `deposit()` functions accept ETH or LSTs and mint `wrsETH` based on a live oracle rate, but provide no `minAmountOut` parameter. If the oracle rate changes between when a user previews the swap and when the transaction executes, the user receives fewer `wrsETH` than expected with no ability to revert. The L1 `LRTDepositPool` already implements this protection via `minRSETHAmountExpected`, making the omission on L2 an inconsistency with an established pattern in the same codebase.

---

### Finding Description

Every L2 pool deposit entry point computes the `wrsETH` amount to mint by calling `viewSwapRsETHAmountAndFee`, which reads the live oracle rate at execution time:

`RSETHPoolV3.sol` ETH deposit: [1](#0-0) 

`RSETHPoolV3.sol` token deposit: [2](#0-1) 

The rate computation: [3](#0-2) 

The same pattern is present in `RSETHPoolV3ExternalBridge.sol`: [4](#0-3) [5](#0-4) 

And in `RSETHPool.sol` (Arbitrum): [6](#0-5) [7](#0-6) 

None of these functions accept a caller-specified minimum output amount. The oracle rate (`getRate()`) is updated periodically via cross-chain messages. If an oracle update is included in the same block or just before the user's transaction, the user receives fewer `wrsETH` than the amount they previewed off-chain, with no mechanism to revert.

By contrast, the L1 `LRTDepositPool` already enforces this protection: [8](#0-7) [9](#0-8) 

The `_beforeDeposit` check at line 667 reverts if `rsethAmountToMint < minRSETHAmountExpected`. No equivalent guard exists in any L2 pool.

---

### Impact Explanation

A user who previews their deposit via `viewSwapRsETHAmountAndFee` and then submits a transaction may receive fewer `wrsETH` than the previewed amount if the oracle rate increases before their transaction is mined. The user's ETH is consumed and the transaction succeeds, but the minted `wrsETH` amount is lower than expected. The user cannot recover the difference. While the economic value of the position is approximately preserved (fewer tokens, each worth more), the contract fails to deliver the token quantity it implicitly promised at preview time. This maps to the **Low** impact category: *Contract fails to deliver promised returns, but doesn't lose value.*

---

### Likelihood Explanation

The rsETH oracle rate is updated regularly via cross-chain rate propagation as staking rewards accrue. Any oracle update that lands in the same block or just before a user's deposit transaction will silently reduce the minted output. This is a routine, non-adversarial occurrence requiring no special conditions or privileged action. Any depositor on any supported L2 (Arbitrum, Base, Linea, Optimism, Scroll, Unichain, etc.) is exposed on every deposit.

---

### Recommendation

Add a `minWrsETHAmountExpected` parameter to all L2 pool `deposit()` functions, mirroring the pattern already used in `LRTDepositPool`:

```solidity
// RSETHPoolV3.sol (and analogous contracts)
function deposit(string memory referralId, uint256 minWrsETHAmountExpected)
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

+   if (rsETHAmount < minWrsETHAmountExpected) revert MinimumAmountToReceiveNotMet();

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same change to the token `deposit()` overload and to the equivalent functions in `RSETHPoolV3ExternalBridge` and `RSETHPool`.

---

### Proof of Concept

1. Oracle rate is `1.05 ETH/rsETH`. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `≈ 0.952 wrsETH` (minus fee).
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction is mined, a cross-chain oracle update sets the rate to `1.10 ETH/rsETH`.
4. User's transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 wrsETH` is minted.
5. User receives `0.909 wrsETH` instead of the previewed `0.952 wrsETH`. The transaction succeeds with no revert, and the user has no recourse.

The root cause is the absence of a minimum output check in `RSETHPoolV3.deposit()` at: [10](#0-9)

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
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
