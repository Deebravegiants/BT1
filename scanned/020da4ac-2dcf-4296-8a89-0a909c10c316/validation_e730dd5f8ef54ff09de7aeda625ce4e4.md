### Title
Missing Slippage Protection in L2 Pool `deposit()` Functions Allows Users to Receive Less rsETH Than Expected - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

---

### Summary

The `deposit()` functions across all L2 pool contracts accept no `minRsETHAmount` parameter. Users have no on-chain mechanism to enforce a minimum amount of wrsETH/rsETH they are willing to accept. The amount minted is determined entirely by the oracle rate at execution time, which can differ from the rate at submission time. This is the direct analog of the Illuminate finding: in both cases the contract fails to honour the user's implicit or explicit output expectation, and the shortfall is structurally guaranteed to occur whenever the rate moves adversely between submission and inclusion.

---

### Finding Description

Every L2 pool variant exposes a public `deposit()` entry point for unprivileged users:

**`RSETHPoolV3ExternalBridge.deposit(string referralId)`** (ETH path): [1](#0-0) 

**`RSETHPoolV3ExternalBridge.deposit(address token, uint256 amount, string referralId)`** (LST path): [2](#0-1) 

In both cases the minted amount is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [3](#0-2) 

`rsETHToETHrate` is read live from the oracle at execution time. There is no `minRsETHAmount` guard anywhere in the call path. The identical pattern exists in `RSETHPool.deposit()` and `RSETHPoolNoWrapper.deposit()`: [4](#0-3) [5](#0-4) 

By contrast, the L1 `LRTDepositPool` correctly accepts and enforces a `minRSETHAmountExpected` parameter: [6](#0-5) [7](#0-6) 

The L2 pools provide no equivalent protection.

---

### Impact Explanation

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who previews `viewSwapRsETHAmountAndFee` off-chain and submits a deposit transaction can receive materially fewer wrsETH tokens than the preview showed if the oracle rate increases between preview and execution. The user's ETH is consumed in full; the shortfall in wrsETH is permanent and unrecoverable within the protocol. The user does not lose ETH in absolute terms (they hold wrsETH worth the same ETH at the new rate), but they receive fewer tokens than they contracted for, which is the same class of harm identified in the Illuminate report.

---

### Likelihood Explanation

**Likelihood: Low.**

The rsETH oracle rate (`getRate()`) reflects the total ETH value restaked in EigenLayer divided by total rsETH supply. This rate increases monotonically as staking rewards accrue and is not directly manipulable by a single transaction. However:

- The rate is updated whenever the L1 oracle is refreshed and the L2 oracle provider propagates the new value cross-chain.
- A user who submits a deposit during a rate-update window can receive significantly less wrsETH than previewed.
- MEV searchers can observe a pending oracle update and sandwich a user's deposit between the oracle update and the user's transaction, guaranteeing the user receives the post-update (worse) rate.

The attack requires no capital beyond gas and is repeatable for every deposit during every oracle update cycle.

---

### Recommendation

Add a `minRsETHAmount` parameter to all `deposit()` overloads in every L2 pool contract, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert SlippageExceeded();

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same change to the token `deposit()` overload and to `RSETHPool` and `RSETHPoolNoWrapper`.

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` wrsETH at the current rate `R`.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is included, the L2 oracle is updated to rate `R' > R` (rsETH is now worth more ETH per token).
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / R'` — strictly less than `X`.
5. Alice receives fewer wrsETH than previewed with no recourse, because there is no `minRsETHAmount` check to revert the transaction.

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
