### Title
No Minimum-Output Parameter in L2 Pool `deposit()` Functions Exposes Users to Oracle-Rate Slippage - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, RSETHPoolV2ExternalBridge.sol, RSETHPool.sol, RSETHPoolNoWrapper.sol)

---

### Summary

Every L2 pool `deposit()` function computes the rsETH output amount solely from the live oracle rate at execution time and provides no caller-supplied minimum-output guard. Because the oracle rate is a mutable on-chain state variable that any account can refresh via the public `LRTOracle.updateRSETHPrice()`, a depositor's transaction can be sandwiched: the attacker refreshes the oracle immediately before the deposit, the deposit executes at the newly-elevated rate, and the user receives materially fewer rsETH tokens than the rate they observed off-chain.

---

### Finding Description

All four L2 pool contracts expose public `deposit()` entry points that follow the same pattern:

```solidity
// RSETHPoolV3ExternalBridge.sol  lines 366-384
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
``` [1](#0-0) 

The output is computed by `viewSwapRsETHAmountAndFee`, which divides the deposit amount by the live oracle rate:

```solidity
// RSETHPoolV3ExternalBridge.sol  lines 418-427
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [2](#0-1) 

`getRate()` reads from `rsETHOracle`, which is backed by `LRTOracle.rsETHPrice` — a state variable updated by the **public, permissionless** `updateRSETHPrice()`:

```solidity
// LRTOracle.sol  line 87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [3](#0-2) 

The same pattern is present in all four pool contracts:

- `RSETHPool.sol` `deposit(string)` and `deposit(address,uint256,string)` [4](#0-3) 
- `RSETHPoolV2ExternalBridge.sol` `deposit(string)` [5](#0-4) 
- `RSETHPoolNoWrapper.sol` `deposit(string)` and `deposit(address,uint256,string)` [6](#0-5) 

By contrast, the L1 `LRTDepositPool` correctly accepts a `minRSETHAmountExpected` parameter on both `depositETH` and `depositAsset`:

```solidity
// LRTDepositPool.sol  lines 76-93
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused ...
``` [7](#0-6) 

The L2 pool contracts have no equivalent guard.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who observes rate R off-chain and submits a deposit expecting `amount / R` rsETH tokens can receive materially fewer tokens if the oracle rate is updated to R′ > R before their transaction executes. Because rsETH is priced at R′ per token, the user's deposited ETH value is preserved in accounting terms, but they receive fewer tokens than the rate they acted on — a broken promise of output. Over time, repeated oracle refreshes timed around large deposits systematically disadvantage depositors relative to the rate they observed.

---

### Likelihood Explanation

`updateRSETHPrice()` is public and callable by any EOA or contract. Rewards accrue continuously in the underlying EigenLayer positions, so the true rsETH price drifts upward between oracle refreshes. A searcher can monitor the mempool for large `deposit()` calls, front-run with `updateRSETHPrice()` to commit the accumulated price increase, and cause the victim's deposit to execute at the elevated rate. No privileged access, no oracle compromise, and no AMM manipulation is required — only a public function call.

---

### Recommendation

Add a `minRsETHAmount` parameter to every `deposit()` overload in all four pool contracts and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool`:

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

Apply the same change to the token-deposit overloads in `RSETHPool`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolNoWrapper`.

---

### Proof of Concept

1. Victim submits `deposit{value: 10 ether}("ref")` to `RSETHPoolV3ExternalBridge`. At submission time `getRate()` returns `1.05e18` (rsETH/ETH), so the victim expects ≈ 9.52 rsETH.
2. Attacker observes the pending transaction. Rewards have accrued since the last oracle update; the true rate is now `1.10e18`.
3. Attacker front-runs with `LRTOracle.updateRSETHPrice()` (public, no access control). `rsETHPrice` is updated to `1.10e18`.
4. Victim's `deposit()` executes. `viewSwapRsETHAmountAndFee` reads `getRate() = 1.10e18` and mints ≈ 9.09 rsETH — 4.5 % fewer tokens than the victim expected.
5. The victim has no recourse; there is no minimum-output check to revert the transaction.

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/pools/RSETHPool.sol (L265-305)
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

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-271)
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
