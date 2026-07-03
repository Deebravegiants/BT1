### Title
Missing Slippage Protection in L2 Pool `deposit()` Allows Users to Receive Fewer rsETH Than Quoted — (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV3.sol)

---

### Summary

The L2 pool `deposit()` functions mint rsETH based on a live oracle rate fetched at execution time, but accept no `minAmountOut` parameter. A user who previews their expected output via `viewSwapRsETHAmountAndFee()` before submitting a transaction can silently receive fewer rsETH than shown, with no on-chain mechanism to reject the changed outcome. This is the direct on-chain analog of the Uniswap wallet bug: the value displayed at "confirmation time" differs from the value actually executed, and the user has no recourse.

---

### Finding Description

Every L2 pool variant exposes a two-step pattern:

**Step 1 — Quote (view):**
```solidity
function viewSwapRsETHAmountAndFee(uint256 amount)
    public view returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [1](#0-0) 

**Step 2 — Execute (state-changing):**
```solidity
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount); // re-reads oracle
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);        // no minAmountOut check
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [2](#0-1) 

The oracle rate is re-fetched inside `deposit()` via `getRate()` → `IOracle(rsETHOracle).getRate()`. If the rate has moved upward between the user's quote and their transaction landing on-chain, the user receives fewer rsETH than shown, with no ability to revert. There is no `minRsETHAmountExpected` parameter.

The same pattern is present in all L2 pool variants: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

By contrast, the L1 `LRTDepositPool` correctly enforces a minimum output:
```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused ...
``` [7](#0-6) 

The L2 pools never adopted this guard.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

A user who previews `viewSwapRsETHAmountAndFee(1 ether)` and sees `rsETHAmount = X` submits `deposit{value: 1 ether}()`. If the oracle rate increases before the transaction is mined (rsETH is now worth more ETH per unit), the user receives `X' < X` rsETH. The ETH is not lost — it is held in the pool — but the user receives fewer liquid restaking tokens than the amount they confirmed in their UI, with no on-chain protection. The shortfall accrues to the pool's ETH balance, benefiting future depositors or the protocol.

---

### Likelihood Explanation

**Medium.** The `rsETHOracle` rate is updated regularly by the manager role (via `InterimRSETHOracle.setRate()`) or by cross-chain rate feeds. Any rate update that lands in the mempool between a user's quote and their deposit transaction will silently reduce the user's output. This is a routine, non-adversarial event that requires no special privileges to trigger — it is simply the normal operation of the oracle system. [8](#0-7) 

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to all L2 pool `deposit()` functions, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert SlippageExceeded();

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same fix to the token-based `deposit(address token, uint256 amount, ...)` overloads in `RSETHPoolV3` and its variants.

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV2`. The oracle returns `rate = 1.05e18`, so she is quoted `~0.952 wrsETH`.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is mined, the manager calls `InterimRSETHOracle.setRate(1.10e18)` (a routine daily update).
4. Alice's transaction mines. `deposit()` re-reads `getRate()` → `1.10e18`, minting only `~0.909 wrsETH`.
5. Alice receives `~4.5%` fewer tokens than the amount she confirmed in the UI. There is no revert, no warning, and no recourse.

The attacker-controlled entry path is the public `deposit()` function itself — any depositor is affected. No privilege escalation is required; the rate update is a normal protocol operation.

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

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L36-44)
```text
    function setRate(uint256 newRate) external onlyRole(MANAGER_ROLE) {
        _setRate(newRate);
    }

    /// @dev Internal function to set the rsETH/ETH rate
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
```
