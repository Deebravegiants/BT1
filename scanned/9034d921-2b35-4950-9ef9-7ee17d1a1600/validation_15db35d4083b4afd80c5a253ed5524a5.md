### Title
No Minimum Output Enforcement in Pool `deposit` Functions Exposes Users to Oracle Rate Drift - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary
Every public-facing `deposit` function across the L2 pool family (`RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) computes the rsETH output amount at execution time using a live oracle rate but accepts **no `minAmountOut` parameter**. A user who previews the swap with `viewSwapRsETHAmountAndFee` and then submits a transaction has no on-chain guarantee that the rate will not have moved by the time the transaction is included, and cannot revert if the received amount falls below their expectation.

---

### Finding Description

All pool `deposit` functions follow the same pattern:

```solidity
// RSETHPoolV3ExternalBridge.sol L366-383
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

The output is computed entirely from `viewSwapRsETHAmountAndFee`, which divides by the live oracle rate:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

The same pattern is present in the token-deposit overload: [3](#0-2) 

And identically in every other pool variant: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

The oracle used for the rsETH/ETH rate is either `ChainlinkOracleForRSETHPoolCollateral` (Chainlink feed, updates on market moves) or `InterimRSETHOracle` (manually updated by MANAGER_ROLE): [8](#0-7) [9](#0-8) 

Because rsETH is a yield-bearing token whose ETH-denominated rate monotonically increases over time, any oracle update that raises `rsETHToETHrate` between a user's quote and their transaction's inclusion will silently reduce `rsETHAmount`. The user has no mechanism to revert the transaction if the received amount is below their acceptable threshold.

By contrast, the mainnet `LRTDepositPool` correctly accepts and enforces a `minRSETHAmountExpected` parameter: [10](#0-9) 

The L2 pool contracts provide a `getMinAmount` helper that computes a slippage-adjusted floor, but it is a **view function only** — it is never called inside `deposit` and provides no on-chain protection: [11](#0-10) 

---

### Impact Explanation

A user who calls `viewSwapRsETHAmountAndFee` off-chain to preview their swap and then submits `deposit` may receive materially fewer wrsETH/rsETH tokens than previewed if the Chainlink feed ticks upward before the transaction is mined. The user's ETH is consumed and the shortfall is irrecoverable. This matches the **"contract fails to deliver promised returns, but doesn't lose value"** impact class (Low).

---

### Likelihood Explanation

The rsETH/ETH rate increases continuously as staking rewards accrue. Chainlink heartbeat updates (typically every 24 h or on 0.5 % deviation) are routine and unpredictable from the user's perspective. On congested L2s, transactions can sit in the mempool long enough for one or more oracle updates to occur. No attacker action is required; the rate drift is a normal protocol property.

---

### Recommendation

Add a `minRSETHAmountExpected` parameter to every `deposit` overload in all pool contracts, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(
    string memory referralId,
    uint256 minRSETHAmountExpected   // <-- add this
) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert MinRSETHAmountNotMet();
    ...
}
```

If backward compatibility requires keeping the existing signature, add a new overload with the slippage parameter and deprecate the old one.

---

### Proof of Concept

1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain. Suppose `rsETHToETHrate = 1.05e18`, so the quoted output is `≈ 0.952 wrsETH`.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the transaction is mined, the Chainlink oracle updates `rsETHToETHrate` to `1.06e18`.
4. `deposit` executes: `rsETHAmount = 1e18 * 1e18 / 1.06e18 ≈ 0.943 wrsETH` — roughly 0.009 wrsETH (~0.95 %) less than quoted.
5. The user receives `0.943 wrsETH` with no revert and no recourse. The gap widens proportionally with larger deposits or larger oracle moves.

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L540-544)
```text
    function getMinAmount(uint256 amount, uint256 slippageTolerance) external pure returns (uint256) {
        if (slippageTolerance > 10_000) revert InvalidSlippageTolerance();

        return amount - (amount * slippageTolerance / 10_000);
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L36-45)
```text
    function setRate(uint256 newRate) external onlyRole(MANAGER_ROLE) {
        _setRate(newRate);
    }

    /// @dev Internal function to set the rsETH/ETH rate
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
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
