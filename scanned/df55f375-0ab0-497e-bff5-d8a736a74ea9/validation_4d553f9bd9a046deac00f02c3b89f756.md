### Title
No Minimum Output Slippage Guard in L2 Pool `deposit()` Functions Exposes Depositors to Oracle Rate Front-Running - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol)

---

### Summary

Every L2 pool `deposit()` function computes the rsETH output amount at execution time using a live oracle rate, but accepts no `minAmountOut` argument. A depositor who previews the rate off-chain and then submits a transaction can receive materially fewer rsETH tokens than expected if the oracle rate is updated before their transaction executes. The L1 `LRTDepositPool` already enforces this protection via `minRSETHAmountExpected`, making the omission in the L2 pools an inconsistency with an established pattern in the same codebase.

---

### Finding Description

All six L2 pool contracts expose public `deposit()` entry points that:

1. Accept ETH or an LST from the caller.
2. Compute the rsETH output by calling `viewSwapRsETHAmountAndFee()`, which reads the live oracle rate via `getRate()` at execution time.
3. Mint or transfer that rsETH amount to the caller.
4. Provide **no parameter** for the caller to express a minimum acceptable output.

`RSETHPoolV3.deposit(string)`: [1](#0-0) 

`RSETHPoolV3.deposit(address,uint256,string)`: [2](#0-1) 

The rsETH amount is determined entirely by the oracle rate at the moment of execution: [3](#0-2) 

The same pattern is present in every other L2 pool: [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

By contrast, the L1 `LRTDepositPool` already enforces a caller-supplied minimum:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) ...
function depositAsset(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected, ...) ...
``` [9](#0-8) 

The oracle rate used by the L2 pools is sourced from `rsETHOracle` and can legitimately change whenever `LRTOracle.updateRSETHPrice()` is called. That function is **public** and callable by any address: [10](#0-9) 

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A depositor who previews the exchange rate with `viewSwapRsETHAmountAndFee()` and then submits a `deposit()` transaction may receive fewer rsETH tokens than the preview indicated. The depositor's ETH/LST is not stolen — it is exchanged at the oracle rate that happens to be live at execution time — but the depositor has no on-chain mechanism to enforce the rate they accepted off-chain. Over time, repeated oracle updates between preview and execution erode the effective yield for active depositors.

---

### Likelihood Explanation

**Medium.**

- `LRTOracle.updateRSETHPrice()` is a permissionless public function. Any address can trigger a price update at any time the oracle is not paused.
- L2 chains (Arbitrum, Base, Optimism, etc.) have public mempools where pending transactions are visible, enabling deliberate front-running of a deposit with an oracle update.
- The rsETH rate is designed to increase monotonically as restaking rewards accrue, so the rate will change regularly in normal operation. Any pending deposit is therefore exposed to rate drift on every block.

---

### Recommendation

Add a `minRSETHAmountExpected` parameter to every L2 pool `deposit()` overload, mirroring the pattern already used in `LRTDepositPool`:

```solidity
// RSETHPoolV3 (and all other L2 pool variants)
function deposit(
    string memory referralId,
    uint256 minRSETHAmountExpected   // <-- add this
) external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER) {
    if (!isEthDepositEnabled) revert EthDepositDisabled();
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

    if (rsETHAmount < minRSETHAmountExpected) revert SlippageExceeded(); // <-- add this

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same change to the token-deposit overload and to all other affected pool contracts.

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` on `RSETHPoolV3` and sees she will receive `X` rsETH at the current oracle rate `R`.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is included, Bob (or a MEV bot) calls `LRTOracle.updateRSETHPrice()` on L1, which propagates a higher rate `R' > R` to the L2 oracle.
4. Alice's transaction executes. `viewSwapRsETHAmountAndFee` now uses `R'`, yielding `X' < X` rsETH.
5. Alice receives `X'` rsETH — fewer than she previewed — with no on-chain recourse, because `deposit()` accepts no minimum output argument.

The gap between `X` and `X'` grows with the magnitude of the oracle update and the size of Alice's deposit. There is no `require` statement that would revert the transaction and return Alice's ETH. [3](#0-2) [10](#0-9)

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

**File:** contracts/LRTDepositPool.sol (L76-118)
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

    /// @notice helps user stake LST to the protocol
    /// @param asset LST asset address to stake
    /// @param depositAmount LST asset amount to stake
    /// @param minRSETHAmountExpected Minimum amount of rseth to receive
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```
