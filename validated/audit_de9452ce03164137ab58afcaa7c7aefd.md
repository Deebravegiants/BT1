### Title
No Minimum Output Protection in `deposit()` Allows Fee Change to Silently Reduce User's rsETH Received - (File: contracts/pools/RSETHPool.sol)

### Summary
The `deposit()` functions across RSETHPool contracts accept ETH or tokens and compute the rsETH output using the live `feeBps` value at execution time. There is no `minAmountOut` parameter. The `DEFAULT_ADMIN_ROLE` can call `setFeeBps()` (and `setTokenFeeBps()`) without a timelock, instantly changing the fee rate. If a fee-increase transaction is included before a user's pending `deposit()`, the user receives fewer rsETH than they previewed — with no on-chain protection.

### Finding Description
Users are expected to call `viewSwapRsETHAmountAndFee()` off-chain to preview how much rsETH they will receive before submitting a `deposit()` transaction. However, the `deposit()` function itself accepts no `minAmountOut` parameter and blindly applies whatever `feeBps` is current at execution time.

In `RSETHPool.sol`, `setFeeBps()` is callable by `DEFAULT_ADMIN_ROLE` with no timelock: [1](#0-0) 

The ETH deposit path computes output entirely from the live `feeBps`: [2](#0-1) 

And the `deposit()` function applies this with no floor check on the output: [3](#0-2) 

The same pattern exists for token deposits via `setTokenFeeBps()` (also `DEFAULT_ADMIN_ROLE`, no timelock): [4](#0-3) 

The same root cause is present in `RSETHPoolV3.sol` (`setFeeBps` by `DEFAULT_ADMIN_ROLE`, max 1000 bps): [5](#0-4) 

And its `deposit()` similarly has no minimum output guard: [6](#0-5) 

### Impact Explanation
A user who previews a swap via `viewSwapRsETHAmountAndFee()` and then submits a `deposit()` transaction can receive materially fewer rsETH tokens than expected if `feeBps` is raised between the preview and execution. The ETH/tokens are not lost (they go to fee accounting), but the user receives a worse exchange rate than they agreed to. This matches the **Low** impact tier: "Contract fails to deliver promised returns, but doesn't lose value."

### Likelihood Explanation
The `DEFAULT_ADMIN_ROLE` can call `setFeeBps()` at any time with no timelock delay. Any legitimate fee adjustment — even a routine one — can race with a user's pending `deposit()` transaction. On L2 chains (Arbitrum, etc.) where these pools are deployed, block times are short and mempool ordering is less predictable, making accidental collisions realistic. No malicious intent is required; a routine governance fee update is sufficient.

### Recommendation
Add a `uint256 minAmountOut` parameter to both `deposit()` overloads and revert if the computed `rsETHAmount` is below it:

```solidity
function deposit(string memory referralId, uint256 minAmountOut) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minAmountOut) revert SlippageExceeded();
    ...
}
```

Apply the same pattern to the token `deposit()` overload and to all other pool contracts that share this pattern (`RSETHPoolV3.sol`, `RSETHPoolV2NBA.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPoolV3ExternalBridge.sol`).

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` and sees they will receive `X` rsETH at the current `feeBps = 10` (0.1%).
2. User submits `deposit{value: 1 ether}(referralId)`.
3. Before the user's transaction is included, admin calls `setFeeBps(1000)` (10%), which executes first.
4. User's `deposit()` executes: `viewSwapRsETHAmountAndFee` now computes with `feeBps = 1000`, returning ~10× less rsETH than previewed.
5. User receives `~0.9 * X` rsETH instead of `~0.999 * X` rsETH — a ~10% shortfall — with no revert or warning.

The entry path is fully unprivileged: any depositor calling the public `deposit()` function is exposed. [3](#0-2) [1](#0-0)

### Citations

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

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L574-578)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
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

**File:** contracts/pools/RSETHPoolV3.sol (L518-522)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```
