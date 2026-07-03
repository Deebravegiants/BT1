### Title
Stale Manually-Set Rate in `InterimRSETHOracle` Enables Over-Minting of rsETH on L2 Pools - (File: contracts/pools/oracle/InterimRSETHOracle.sol)

### Summary
`InterimRSETHOracle` stores a manually set rsETH/ETH rate with no last-updated timestamp and no staleness guard. Every L2 pool contract (`RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`) reads this rate unconditionally via `IOracle(rsETHOracle).getRate()` to compute how many rsETH tokens to mint per deposited ETH. If the manager fails to update the rate while the true rsETH/ETH exchange rate rises, any depositor receives more rsETH than they are entitled to, diluting existing holders.

### Finding Description
`InterimRSETHOracle` is a production contract (located in `contracts/pools/oracle/`) that stores a single `uint256 public rate` set by a privileged `MANAGER_ROLE` account. [1](#0-0) 

The `getRate()` function returns this value with no freshness check: [2](#0-1) 

There is no `lastUpdated` mapping, no maximum staleness window, and no revert path if the rate has not been refreshed within a reasonable period.

Every pool's `deposit()` path calls `viewSwapRsETHAmountAndFee()`, which divides the deposited amount by the oracle rate: [3](#0-2) [4](#0-3) 

The same pattern appears in `RSETHPoolV2NBA`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`. [5](#0-4) [6](#0-5) 

Because `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`, a stale (too-low) rate produces a larger `rsETHAmount` than the depositor deserves.

### Impact Explanation
**High — Theft of unclaimed yield.**

When the true rsETH/ETH rate has risen (rsETH has accrued staking rewards) but the oracle rate has not been updated, every new depositor receives more rsETH than their ETH contribution warrants. This dilutes the share value of all existing rsETH holders, effectively transferring accrued yield from existing holders to new depositors. The magnitude scales with the size of deposits and the duration of staleness.

### Likelihood Explanation
**Medium.**

The `InterimRSETHOracle` is explicitly described as an interim solution pending a more robust oracle. Manual rate updates depend on operational availability of the `MANAGER_ROLE` key. Network congestion, key unavailability, or simple operational oversight can delay updates. rsETH accrues staking rewards continuously, so even a few hours of staleness during a high-yield period creates a meaningful discrepancy. Any unprivileged depositor can exploit this passively by depositing during a staleness window — no special knowledge or front-running is required.

### Recommendation
1. **Add a `lastUpdated` timestamp** to `InterimRSETHOracle` and record it in `_setRate()`.
2. **Add a staleness guard** in `getRate()` that reverts (or returns 0) if `block.timestamp - lastUpdated > MAX_STALENESS` (e.g., 24 hours).
3. **Longer term**, replace `InterimRSETHOracle` with a live on-chain oracle (e.g., a Chainlink feed or a cross-chain message from `LRTOracle`) so the rate tracks the true rsETH/ETH exchange rate without manual intervention.

### Proof of Concept

1. `InterimRSETHOracle` is deployed and configured as `rsETHOracle` in `RSETHPoolV2` with `rate = 1.05e18`.
2. rsETH accrues staking rewards; the true rate rises to `1.10e18`. The manager does not call `setRate()`.
3. An attacker calls `RSETHPoolV2.deposit{value: 1 ether}("")`.
4. Inside `viewSwapRsETHAmountAndFee(1e18)`:
   - `fee = 1e18 * feeBps / 10_000` (assume 0 for simplicity)
   - `rsETHToETHrate = getRate()` → returns stale `1.05e18`
   - `rsETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.9524 rsETH`
5. At the correct rate `1.10e18`, the attacker should receive `1e18 * 1e18 / 1.10e18 ≈ 0.9091 rsETH`.
6. The attacker receives **~0.0433 extra rsETH** per ETH deposited, extracted from the yield accrued by existing holders.
7. This is repeatable by any depositor for the entire duration of the staleness window. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L14-15)
```text
    /// @notice The current rsETH/ETH rate
    uint256 public rate;
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L40-51)
```text
    /// @dev Internal function to set the rsETH/ETH rate
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
    }

    /// @notice Get the current rsETH/ETH rate
    /// @return The current rate
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-233)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev view function to get the rsETH amount for a given amount of ETH
    /// @param amount The amount of ETH
    /// @return rsETHAmount The amount of rsETH that will be received
    /// @return fee The fee that will be charged
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L99-132)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }

    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev view function to get the rsETH amount for a given amount of ETH
    /// @param amount The amount of ETH
    /// @return rsETHAmount The amount of rsETH that will be received
    /// @return fee The fee that will be charged
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L271-273)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```
