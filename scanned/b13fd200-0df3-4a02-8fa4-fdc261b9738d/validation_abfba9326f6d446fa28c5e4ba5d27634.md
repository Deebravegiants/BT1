### Title
No Deadline or Minimum Output Parameter in Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV2.sol, contracts/agETH/AGETHPoolV3.sol)

### Summary
All publicly accessible `deposit()` functions across the L2 pool contracts accept ETH or supported tokens and mint/transfer rsETH (or agETH) to the caller, but provide **no deadline parameter and no minimum output amount parameter**. A transaction submitted to the mempool can remain pending indefinitely and execute at a later time when the rsETH/ETH exchange rate has increased, resulting in the user receiving fewer rsETH than they anticipated at submission time, with no on-chain protection to revert the trade.

### Finding Description
The `deposit()` functions in `RSETHPoolNoWrapper`, `RSETHPool`, `RSETHPoolV3`, `RSETHPoolV2`, and `AGETHPoolV3` compute the output amount at execution time using the live oracle rate:

```solidity
// RSETHPoolNoWrapper.sol – ETH deposit
function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    rsETH.safeTransfer(msg.sender, rsETHAmount);
}
```

```solidity
// viewSwapRsETHAmountAndFee
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Because `rsETHToETHrate` is fetched from the oracle at the moment of execution, and rsETH is a yield-bearing token whose rate increases monotonically over time, any delay between transaction submission and inclusion results in a higher rate and therefore fewer rsETH minted per unit of ETH. Neither a `deadline` parameter nor a `minRsETHAmountExpected` parameter is present in any of these functions, so the user has no on-chain mechanism to bound the acceptable output or to expire the transaction.

This contrasts with `LRTDepositPool.depositETH()` and `LRTDepositPool.depositAsset()` on L1, which both accept a `minRSETHAmountExpected` parameter that reverts if the minted amount falls below the caller's threshold.

### Impact Explanation
A user who submits a deposit transaction during a period of low gas prices (or network congestion on the L2 sequencer) may have their transaction executed hours or days later. Because the rsETH/ETH rate increases continuously, the user receives fewer rsETH than they expected at submission time. The ETH principal value is preserved (fewer rsETH, each worth more ETH), so there is no direct ETH loss, but the user does not receive the rsETH quantity they intended. This maps to **Low** severity: the contract fails to deliver the promised token quantity, but does not lose the deposited value.

For token deposits (e.g., wstETH), if the token's oracle rate changes adversely while the transaction is pending, the discrepancy can be larger.

### Likelihood Explanation
L2 sequencers (Arbitrum, Optimism, Base, etc.) can experience congestion spikes (e.g., during high-activity events), causing transactions to queue. The rsETH rate increases every epoch as staking rewards accrue, so any non-trivial delay produces a measurable shortfall. The affected functions are the primary user-facing entry points for all L2 pool contracts, making this reachable by any depositor.

### Recommendation
1. Add a `uint256 minRsETHAmountExpected` parameter to all `deposit()` overloads and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool.depositETH()` and `LRTDepositPool.depositAsset()`.
2. Optionally add a `uint256 deadline` parameter and revert with `block.timestamp > deadline`.

### Proof of Concept

1. Alice calls `RSETHPoolNoWrapper.deposit{value: 1 ether}("ref")` when `rsETHToETHrate = 1.05e18`, expecting to receive `≈ 0.952 rsETH`.
2. The transaction sits in the mempool for 48 hours due to sequencer congestion.
3. Staking rewards accrue; `rsETHToETHrate` rises to `1.06e18`.
4. The transaction is included. Alice receives `1e18 * 1e18 / 1.06e18 ≈ 0.943 rsETH` — roughly 0.9% fewer tokens than expected, with no revert and no recourse.
5. Because there is no `minRsETHAmountExpected` check and no `deadline`, the contract silently accepts the worse rate.

**Affected functions (no minimum output, no deadline):** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

**Contrast with the protected L1 pattern:** [5](#0-4)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L244-252)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
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
