### Title
Missing Minimum Output Amount (Slippage Protection) in All L2 Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

Every L2 deposit pool in the LRT-rsETH protocol exposes a `deposit()` function that mints `wrsETH` (or transfers `rsETH`) to the caller at the current oracle rate, but accepts **no `minAmountOut` parameter**. Users are unconditionally committed to whatever exchange rate the oracle reports at execution time, with no on-chain mechanism to reject an unfavorable rate. This is the direct analog of the Connext "no cancel on destination domain" class: users are forced to accept any slippage with no recourse.

---

### Finding Description

All six L2 pool variants share the same structural omission. Taking `RSETHPoolV3ExternalBridge` as the canonical example:

```solidity
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);          // ← no minAmountOut guard
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

The `rsETHAmount` is computed entirely from the oracle rate:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount)
    public view returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();             // ← cross-chain oracle, can be stale
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

The oracle rate (`rsETHOracle`) is a cross-chain rate pushed from L1 to L2 with inherent latency. If the rate is stale (rsETH has appreciated on L1 but the L2 oracle has not yet been updated), `rsETHToETHrate` is artificially high, and `rsETHAmount` is correspondingly lower than the fair value. The user's ETH is consumed and `wrsETH` is minted at the unfavorable rate — there is no `minAmountOut` check, no revert path, and no cancel/refund mechanism.

The identical omission exists in every pool variant:

- `RSETHPoolV3.deposit()` — both ETH and token overloads
- `RSETHPoolV3ExternalBridge.deposit()` — both ETH and token overloads
- `RSETHPoolV3WithNativeChainBridge.deposit()` — both ETH and token overloads
- `RSETHPool.deposit()` — both ETH and token overloads
- `RSETHPoolNoWrapper.deposit()` — both ETH and token overloads
- `RSETHPoolV2ExternalBridge.deposit()` — ETH overload

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but does not lose value.**

A user who submits a `deposit()` transaction when the oracle shows a fair rate may have the transaction executed after the oracle has drifted upward (rsETH appreciated on L1 but L2 oracle not yet updated). The user receives fewer `wrsETH` than the fair rate would entitle them to. The ETH is not lost from the protocol — it is held in the pool and eventually bridged to L1 — but the user's share of the protocol is permanently diluted relative to what they should have received. There is no on-chain path for the user to reject the execution and recover their ETH.

---

### Likelihood Explanation

**Medium.** The rsETH exchange rate is computed on L1 by `LRTOracle` and pushed to L2 via a cross-chain rate provider. This push is not atomic with user deposits; there is always a window of staleness. In periods of rapid LST price movement or EigenLayer reward accrual, the L2 oracle can lag the true L1 rate by a meaningful margin. Any user depositing during this window receives fewer `wrsETH` than they would at the correct rate, with no ability to protect themselves.

---

### Recommendation

Add a `minAmountOut` parameter to all `deposit()` overloads in every pool contract. After computing `rsETHAmount`, revert if it falls below the caller-specified minimum:

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

Apply the same pattern to the token-deposit overloads and to all other pool variants.

---

### Proof of Concept

1. The L2 oracle reports `rsETHToETHrate = 1.10e18` (stale; true L1 rate is `1.05e18`).
2. User calls `deposit{value: 1 ether}("")` on `RSETHPoolV3ExternalBridge`.
3. `viewSwapRsETHAmountAndFee(1e18)` computes `rsETHAmount = 1e18 * 1e18 / 1.10e18 ≈ 0.909 wrsETH`.
4. At the true rate the user should receive `1e18 * 1e18 / 1.05e18 ≈ 0.952 wrsETH`.
5. The user loses ~4.5% of their expected output with no on-chain recourse.
6. The transaction cannot be reverted after execution; there is no cancel function. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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
