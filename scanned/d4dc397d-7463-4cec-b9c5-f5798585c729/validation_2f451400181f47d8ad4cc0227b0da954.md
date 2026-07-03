### Title
Stale `InterimRSETHOracle` Rate Enables Over-Minting of wrsETH Relative to ETH Backing, Undercollateralizing the Wrapper — (File: `contracts/pools/oracle/InterimRSETHOracle.sol`)

---

### Summary

The `InterimRSETHOracle` stores a manually-set rsETH/ETH exchange rate with no on-chain staleness check. All L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPool`, `RSETHPoolNoWrapper`) use this rate to calculate how many wrsETH tokens to mint for a given ETH deposit. Because rsETH/ETH appreciates monotonically over time (staking rewards), the stored rate inevitably lags behind the true rate between manual updates. An unprivileged depositor can exploit this lag to receive more wrsETH than the deposited ETH can back when converted to rsETH on L1, undercollateralizing the wrsETH wrapper.

---

### Finding Description

`InterimRSETHOracle` is the oracle used by L2 pool contracts to price ETH→wrsETH swaps. Its `getRate()` function returns a raw stored value with no freshness validation: [1](#0-0) 

The rate is updated only when a `MANAGER_ROLE` account calls `setRate()`: [2](#0-1) 

Every L2 pool contract calls `IOracle(rsETHOracle).getRate()` inside `viewSwapRsETHAmountAndFee` to compute the wrsETH amount to mint: [3](#0-2) 

The same pattern is present in `RSETHPoolV3`: [4](#0-3) 

And in `RSETHPoolNoWrapper`: [5](#0-4) 

The minted amount is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
```

If `rsETHToETHrate` is stale (lower than the true current rate), `rsETHAmount` is inflated — more wrsETH is minted than the deposited ETH can back when bridged to L1 and converted to rsETH at the current (higher) rate.

The `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` mint wrsETH directly: [6](#0-5) 

The deposited ETH accumulates in the pool and is later bridged to L1 via `bridgeAssets()` or `bridgeAssetsViaNativeBridge()`. On L1, it is deposited into `LRTDepositPool` at the current (higher) rsETH/ETH rate, minting fewer rsETH than the wrsETH already issued on L2. The wrsETH wrapper becomes undercollateralized by the difference.

---

### Impact Explanation

**Impact: Medium — Contract fails to deliver promised returns / Temporary freezing of unclaimed yield.**

When the oracle rate is stale by Δ (e.g., rsETH has appreciated by 0.5% since the last manual update), every depositor receives approximately 0.5% more wrsETH than the ETH they deposited can back. The wrsETH wrapper's rsETH backing is insufficient to honor all redemptions at par. Existing wrsETH holders' redemption value is diluted. The magnitude scales with: (1) the size of deposits during the stale window, (2) the duration of staleness, and (3) the daily mint limit.

---

### Likelihood Explanation

**Likelihood: Medium.**

rsETH/ETH rate increases continuously as staking rewards accrue (~4–5% APY, ~0.01% per day). The `InterimRSETHOracle` is explicitly described as "an interim solution until a more robust oracle is implemented," implying infrequent manual updates. Any gap between updates — even hours — creates an exploitable window. An unprivileged depositor needs only to observe that the L2 oracle rate is lower than the L1 `LRTOracle.rsETHPrice` and deposit ETH during that window. No special access is required. [7](#0-6) 

---

### Recommendation

1. Add an on-chain staleness check to `InterimRSETHOracle.getRate()` that reverts if the rate has not been updated within a configurable maximum age (e.g., 24 hours). Store a `lastUpdatedAt` timestamp alongside `rate`.
2. Replace `InterimRSETHOracle` with a cross-chain rate feed (e.g., a LayerZero-based rate distributor that pushes the L1 `rsETHPrice` to L2) as soon as possible.
3. Add a minimum-output parameter (`minRsETHAmount`) to the `deposit()` functions so users can protect themselves against receiving fewer tokens than expected due to rate changes.

---

### Proof of Concept

1. L1 `LRTOracle.rsETHPrice` = `1.10e18` (rsETH is worth 1.10 ETH).
2. L2 `InterimRSETHOracle.rate` = `1.05e18` (stale — manager has not updated it).
3. Attacker calls `RSETHPoolV3ExternalBridge.deposit{value: 100 ether}("")`.
4. `viewSwapRsETHAmountAndFee(100e18)` computes:
   - `fee = 100e18 * feeBps / 10_000` (e.g., 0 if feeBps=0)
   - `rsETHAmount = 100e18 * 1e18 / 1.05e18 = 95.238 wrsETH`
5. Fair value at true rate: `100e18 * 1e18 / 1.10e18 = 90.909 wrsETH`.
6. Attacker receives **4.329 excess wrsETH** (≈4.76% overmint).
7. The 100 ETH is later bridged to L1 and deposited, minting only `90.909 rsETH` to back `95.238 wrsETH`.
8. The wrsETH wrapper is undercollateralized by `4.329 rsETH` worth of value.
9. Attacker redeems `95.238 wrsETH` for `~95.238 * 1.10 = 104.76 ETH` worth of rsETH, extracting `~4.76 ETH` from existing rsETH holders. [8](#0-7) [9](#0-8) [3](#0-2)

### Citations

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L8-10)
```text
/// @title InterimRSETHOracle Contract
/// @notice contract where the owner sets the rsETH/ETH rate manually
/// @dev This contract is used as an interim solution until a more robust oracle is implemented
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L36-38)
```text
    function setRate(uint256 newRate) external onlyRole(MANAGER_ROLE) {
        _setRate(newRate);
    }
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L41-51)
```text
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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
