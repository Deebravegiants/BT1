### Title
Lack of Slippage Control in `RSETHPoolV3::deposit` Functions Can Lead to Unexpected Financial Losses for Users - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper` contracts expose `deposit` functions that calculate the rsETH output amount from an oracle rate at execution time, but provide no mechanism for users to specify a minimum rsETH amount to receive. If the oracle rate changes between transaction submission and execution, users silently receive fewer rsETH tokens than expected with no ability to revert.

### Finding Description
The `RSETHPoolV3.deposit` functions (both ETH and token variants) compute the rsETH output via `viewSwapRsETHAmountAndFee`, which reads the live oracle rate at execution time. No `minRsETHAmount` parameter exists, so users cannot enforce a lower bound on the tokens they receive.

```solidity
// RSETHPoolV3.sol L246-265 (ETH deposit)
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    if (!isEthDepositEnabled) revert EthDepositDisabled();
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // ← no minimum check
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

The rate used is:
```solidity
// RSETHPoolV3.sol L299-308
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // ← live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

The same pattern is present in the token deposit overload and in all three pool variants: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

By contrast, the upstream `LRTDepositPool` correctly enforces a `minRSETHAmountExpected` guard: [10](#0-9) 

The pool contracts are the user-facing entry points on L2 chains and do not inherit this protection.

### Impact Explanation
When a user's transaction is pending in the mempool and the rsETH oracle rate increases (rsETH appreciates in ETH terms), the user receives fewer wrsETH tokens than they observed when constructing the transaction. Because the user has already sent ETH (irreversible), they cannot cancel. The received wrsETH is worth the deposited ETH minus fees, so no ETH value is destroyed, but the user receives fewer tokens than promised — matching the **Low: Contract fails to deliver promised returns, but doesn't lose value** impact tier.

### Likelihood Explanation
Oracle rate updates for rsETH occur regularly as the underlying staked ETH accrues rewards. Any user whose transaction is delayed (network congestion, gas price underbid) between the moment they preview the rate and the moment the transaction is mined is exposed. This is a routine on-chain condition, not a contrived attack, making the likelihood **Medium** for any active depositor.

### Recommendation
Add a `minRsETHAmount` parameter to both `deposit` overloads in all pool contracts and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool._beforeDeposit`:

```diff
- function deposit(string memory referralId)
+ function deposit(uint256 minRsETHAmount, string memory referralId)
      external payable nonReentrant whenNotPaused
      limitDailyMint(msg.value, ETH_IDENTIFIER)
  {
      ...
      (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
+     if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
      ...
  }

- function deposit(address token, uint256 amount, string memory referralId)
+ function deposit(address token, uint256 amount, uint256 minRsETHAmount, string memory referralId)
      external nonReentrant whenNotPaused onlySupportedToken(token)
      limitDailyMint(amount, token)
  {
      ...
      (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
+     if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
      ...
  }
```

Apply the same fix to `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper`.

### Proof of Concept
1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive 0.95 wrsETH at the current oracle rate.
2. Alice submits `deposit{value: 1 ether}("ref")` with a competitive but not top-of-block gas price.
3. Before Alice's transaction is mined, the rsETH oracle rate updates (rsETH appreciates).
4. Alice's transaction executes: `viewSwapRsETHAmountAndFee` now returns 0.90 wrsETH at the new rate.
5. Alice receives 0.90 wrsETH — 5% fewer tokens than expected — with no revert and no recourse, because no minimum output check exists. [11](#0-10)

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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L307-329)
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
