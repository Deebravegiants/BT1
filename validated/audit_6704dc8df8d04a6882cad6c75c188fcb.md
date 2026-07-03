### Title
Stale `rsETHPrice` Due to No Automated Update Mechanism Allows Depositors to Receive Excess rsETH, Stealing Yield from Existing Holders - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public function that must be called manually to update the stored `rsETHPrice`. There is no automated or on-chain mechanism guaranteeing timely invocation. When `rsETHPrice` is stale (lower than the true value, as EigenLayer staking rewards accumulate), any depositor calling `LRTDepositPool.depositETH()` or `depositAsset()` receives more rsETH than they are entitled to, diluting existing rsETH holders and stealing their accrued yield. The same stale rate is propagated to L2 chains via `RSETHMultiChainRateProvider`/`RSETHRateProvider`, compounding the impact across all L2 pool depositors.

### Finding Description

`LRTOracle` stores a cached exchange rate in the state variable `rsETHPrice`: [1](#0-0) 

This value is updated only when `updateRSETHPrice()` (public) or `updateRSETHPriceAsManager()` (manager-only) is explicitly called: [2](#0-1) 

There is no automated trigger — no hook in `depositETH`, no keeper, no time-based callback. The function is called from exactly zero protocol-internal paths on every user interaction.

`LRTDepositPool.getRsETHAmountToMint()` divides by the cached `rsETHPrice` to compute how many rsETH tokens to mint: [3](#0-2) 

When `rsETHPrice` is stale-low (i.e., EigenLayer rewards have accrued but the price has not been updated), the denominator is smaller than the true value, so `rsethAmountToMint` is inflated. New depositors receive more rsETH than their ETH contribution warrants, diluting all existing holders.

Additionally, `_updateRsETHPrice()` computes the protocol fee using the stale price as the TVL baseline: [4](#0-3) 

A stale (understated) `rsETHPrice` causes `previousTVL` to be understated, inflating `rewardAmount` and thus `protocolFeeInETH`. When the update is finally called, the protocol mints more rsETH as fee than it is entitled to, further diluting holders.

The same stale value is read by the cross-chain rate providers and propagated to all L2 chains: [5](#0-4) [6](#0-5) 

L2 pools (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) call `IOracle(rsETHOracle).getRate()` to compute wrsETH mint amounts: [7](#0-6) 

A stale rate on L2 means L2 depositors also receive excess wrsETH.

Furthermore, `pricePercentageLimit` can cause `updateRSETHPrice()` to revert for non-manager callers when the price has moved beyond the configured threshold: [8](#0-7) 

This means that during periods of significant reward accrual, only the manager can update the price, and if the manager delays, the staleness window grows.

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders continuously accrue yield as EigenLayer staking rewards increase the protocol's ETH TVL. When `rsETHPrice` is stale, new depositors receive rsETH at the old (lower) price, minting more tokens than their deposit warrants. This dilutes the share of existing holders, transferring their accrued yield to new depositors. The same effect applies on every L2 chain where the stale rate has been propagated. Additionally, the inflated fee calculation mints excess rsETH to the treasury, further diluting holders.

### Likelihood Explanation

**Medium.** EigenLayer staking rewards accrue continuously. There is no on-chain mechanism that calls `updateRSETHPrice()` on every deposit or on any schedule. Any gap between reward accrual and price update creates an exploitable window. A sophisticated depositor can monitor the on-chain TVL vs. the cached `rsETHPrice` and deposit precisely when the gap is largest, maximizing the excess rsETH received. The `pricePercentageLimit` guard can additionally block public callers from correcting the price, extending the staleness window without manager intervention.

### Recommendation

1. Call `updateRSETHPrice()` atomically at the start of `depositETH()` and `depositAsset()` in `LRTDepositPool`, so the price is always fresh before computing the mint amount.
2. Similarly, call `updateRSETHPrice()` before computing withdrawal amounts in `LRTWithdrawalManager`.
3. Consider integrating a keeper or Chainlink Automation job to call `updateRSETHPrice()` on a regular cadence (e.g., every 24 hours) independent of user activity.
4. On L2, ensure `updateRate()` on the rate provider is called frequently enough that the L2 oracle rate does not lag the L1 price by more than an acceptable threshold.

### Proof of Concept

1. At time T₀, `rsETHPrice = 1.05e18` (reflecting prior EigenLayer rewards). `updateRSETHPrice()` is not called for 7 days.
2. Over 7 days, EigenLayer rewards increase the protocol's ETH TVL by 0.5%. The true rsETH price is now `≈ 1.0553e18`, but `rsETHPrice` remains `1.05e18`.
3. Alice calls `LRTDepositPool.depositETH{value: 100 ether}("")`.
4. `getRsETHAmountToMint` computes: `100e18 * 1e18 / 1.05e18 ≈ 95.238 rsETH` (using stale price).
5. True fair amount: `100e18 * 1e18 / 1.0553e18 ≈ 94.762 rsETH`.
6. Alice receives `≈ 0.476 rsETH` excess — stolen from existing holders' accrued yield.
7. When `updateRSETHPrice()` is finally called, `previousTVL` is computed using the stale `1.05e18` price, overstating `rewardAmount` and causing the protocol to mint excess fee rsETH to the treasury, further diluting holders.
8. If `RSETHMultiChainRateProvider.updateRate()` was called during the staleness window, all L2 pools also used the stale rate, compounding the dilution across chains.

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L233-246)
```text
        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
```

**File:** contracts/LRTOracle.sol (L256-265)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L26-28)
```text
    /// @notice Returns the latest rate from the rsETH contract
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
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
