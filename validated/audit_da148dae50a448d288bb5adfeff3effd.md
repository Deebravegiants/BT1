### Title
L2 Pool `deposit()` Functions Lack User-Configurable Minimum Output Parameter Present in L1 `LRTDepositPool` - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPool.sol)

---

### Summary

The L1 `LRTDepositPool.depositETH()` correctly accepts a `minRSETHAmountExpected` parameter, allowing users to specify the minimum rsETH they will accept and revert if the oracle rate has moved unfavorably. All L2 pool `deposit()` functions — `RSETHPoolV3ExternalBridge`, `RSETHPoolV3`, `RSETHPoolV2ExternalBridge`, and `RSETHPool` — omit this parameter entirely, effectively hardcoding the minimum output to zero. Any depositor on L2 has no protection against oracle rate changes between transaction submission and execution.

---

### Finding Description

`LRTDepositPool.depositETH()` on L1 enforces a user-supplied floor:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable ...
{
    uint256 rsethAmountToMint = _beforeDeposit(
        LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected
    );
    ...
}
```

Inside `_beforeDeposit`, the check is:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [1](#0-0) [2](#0-1) 

Every L2 pool `deposit()` function is missing this guard. For example, in `RSETHPoolV3ExternalBridge`:

```solidity
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [3](#0-2) 

The same pattern is repeated for token deposits and across all other L2 pool variants: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

The output amount is computed solely from the oracle rate at execution time:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [8](#0-7) 

There is no floor check. The minimum output is implicitly hardcoded to zero.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

A user who previews the exchange rate off-chain and submits a `deposit()` transaction may receive materially fewer wrsETH/rsETH than expected if the `rsETHOracle` rate is updated between submission and inclusion. The deposited ETH is not lost — it remains in the pool — but the user receives fewer liquid restaking tokens than the rate they observed, with no on-chain mechanism to revert the transaction. On L1, the identical scenario is protected by `minRSETHAmountExpected`; on L2 it is not.

---

### Likelihood Explanation

**Low.** The `rsETHOracle` rate is protocol-controlled and changes gradually as EigenLayer rewards accrue and underlying LST prices shift. It does not change with every block like an AMM price. However, the rate does change across blocks, and a user whose transaction is delayed in the mempool (e.g., during congestion) or whose transaction is reordered can receive a worse rate than previewed. The absence of any floor makes every L2 deposit subject to this risk with no opt-out.

---

### Recommendation

Add a `minRsETHAmount` parameter to every L2 pool `deposit()` function, mirroring the L1 pattern:

```diff
- function deposit(string memory referralId)
-     external payable nonReentrant whenNotPaused
-     limitDailyMint(msg.value, ETH_IDENTIFIER)
+ function deposit(uint256 minRsETHAmount, string memory referralId)
+     external payable nonReentrant whenNotPaused
+     limitDailyMint(msg.value, ETH_IDENTIFIER)
  {
      uint256 amount = msg.value;
      if (amount == 0) revert InvalidAmount();
      (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
+     if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
      feeEarnedInETH += fee;
      wrsETH.mint(msg.sender, rsETHAmount);
      emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
  }
```

Apply the same change to the token-deposit overloads in all four pool contracts.

---

### Proof of Concept

1. The current rsETH/ETH oracle rate is `R`. A user calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees they will receive `X` wrsETH.
2. The user submits `deposit{value: 1 ether}("ref")` to `RSETHPoolV3ExternalBridge`.
3. Before the transaction is included, the protocol oracle is updated; the new rate is `R' > R` (rsETH is now worth more ETH, so fewer wrsETH are minted per ETH).
4. The transaction executes. `viewSwapRsETHAmountAndFee` now returns `X' < X`. Because there is no minimum-output check, `wrsETH.mint(msg.sender, X')` succeeds.
5. The user receives `X'` wrsETH instead of the `X` they previewed, with no revert and no recourse.
6. On L1, the same scenario would revert with `MinimumAmountToReceiveNotMet` if the user had set `minRSETHAmountExpected = X`.

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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
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
