### Title
Nested Unbounded Loop in `updateRSETHPrice()` Can Cause Permanent Out-of-Gas, Freezing Fee Yield and Price Protection - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public function that internally executes a deeply nested loop: for every supported asset, for every NodeDelegator, it calls `NodeDelegator.getAssetUnstaking()`, which in turn iterates over all queued EigenLayer withdrawals and their strategies. As the protocol scales and accumulates more queued EigenLayer withdrawals, this call chain will eventually exceed the block gas limit, permanently preventing price updates, freezing fee yield accrual, and disabling the automatic price-drop pause protection.

---

### Finding Description

The public function `LRTOracle.updateRSETHPrice()` triggers the following nested call chain:

**Step 1 — `LRTOracle._getTotalEthInProtocol()`** iterates over every supported asset:

```
// LRTOracle.sol line 336
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    ...
}
```

**Step 2 — `LRTDepositPool.getAssetDistributionData()`** iterates over every NodeDelegator in `nodeDelegatorQueue`:

```
// LRTDepositPool.sol line 447
for (uint256 i; i < ndcsCount;) {
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
```

The same pattern repeats in `getETHDistributionData()` at line 484–492.

**Step 3 — `NodeDelegator.getAssetUnstaking()`** fetches ALL queued EigenLayer withdrawals for the NDC and iterates over them with a nested inner loop over strategies:

```
// NodeDelegator.sol line 406–426
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, ...) =
    _getDelegationManager().getQueuedWithdrawals(address(this));

for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
        ...
    }
}
```

The total iteration count is: `supportedAssets × NDCs × queuedWithdrawals_per_NDC × strategies_per_withdrawal`.

The `queuedWithdrawals` array returned by EigenLayer's `DelegationManager.getQueuedWithdrawals()` contains every withdrawal that has been queued but not yet completed. As the protocol operates — queuing EigenLayer withdrawals to service user unstaking requests — this array grows continuously. There is no cap on the number of concurrent queued withdrawals per NDC. The `nodeDelegatorQueue` is bounded by `maxNodeDelegatorLimit` (default 10, admin-raisable), and `supportedAssets` is admin-controlled, but the innermost dimension (`queuedWithdrawals`) is unbounded and grows with normal protocol operation.

---

### Impact Explanation

When `updateRSETHPrice()` runs out of gas:

1. **Permanent freezing of unclaimed yield**: The fee minting logic inside `_updateRsETHPrice()` (lines 299–311) never executes. Protocol fees in the form of rsETH are never minted to the treasury. This is a permanent freeze of unclaimed yield for as long as the condition persists.

2. **Price protection disabled**: The automatic pause-on-price-drop mechanism (lines 270–282) that calls `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` on the oracle can never trigger. If the protocol's TVL drops (e.g., slashing event), the safety circuit breaker is silently broken.

3. **Stale rsETH price**: The stored `rsETHPrice` state variable becomes permanently stale. Deposits via `depositETH`/`depositAsset` read this stale value via `getRsETHAmountToMint()` (line 520), causing users to mint rsETH at an incorrect exchange rate.

Impact classification: **Medium — Permanent freezing of unclaimed yield** and **Medium — Unbounded gas consumption**.

---

### Likelihood Explanation

The LRT-rsETH protocol actively queues EigenLayer withdrawals to service user unstaking requests via `LRTWithdrawalManager`. Each queued withdrawal remains in EigenLayer's pending queue for the withdrawal delay period (currently 7 days on mainnet). During periods of high withdrawal activity, many concurrent queued withdrawals accumulate per NDC. With multiple NDCs (up to `maxNodeDelegatorLimit`) and multiple supported assets, the gas cost of `updateRSETHPrice()` grows proportionally. This is a natural consequence of normal protocol operation at scale, not a contrived attack scenario. The likelihood increases monotonically as protocol TVL and withdrawal volume grow.

---

### Recommendation

1. **Decouple `getAssetUnstaking` from the price update path.** Cache the queued unstaking amount in a storage variable that is updated lazily (e.g., when withdrawals are queued or completed), rather than recomputing it by iterating over all EigenLayer queued withdrawals on every price update.

2. **Cap the number of concurrent queued withdrawals per NDC** by enforcing a maximum in the withdrawal queuing logic, analogous to how `maxNodeDelegatorLimit` caps the NDC count.

3. **Paginate or batch the price update** so that it can be called incrementally if the full computation exceeds a safe gas budget.

---

### Proof of Concept

Call trace that demonstrates the nested unbounded iteration:

```
updateRSETHPrice()                          [LRTOracle.sol:87]  — public, no auth
  └─ _updateRsETHPrice()                   [LRTOracle.sol:214]
       └─ _getTotalEthInProtocol()          [LRTOracle.sol:331]
            └─ for each supportedAsset:     [LRTOracle.sol:336]
                 └─ getTotalAssetDeposits() [LRTDepositPool.sol:385]
                      └─ getAssetDistributionData() [LRTDepositPool.sol:426]
                           └─ for each NDC in nodeDelegatorQueue: [LRTDepositPool.sol:447]
                                └─ getAssetUnstaking(asset) [NodeDelegator.sol:405]
                                     └─ getQueuedWithdrawals() → unbounded array
                                          └─ for each withdrawal:  [NodeDelegator.sol:409]
                                               └─ for each strategy: [NodeDelegator.sol:412]
                                                    └─ sharesToUnderlyingView() [external call]
```

Concrete scenario: 3 supported assets × 5 NDCs × 50 queued withdrawals per NDC × 3 strategies per withdrawal = 2,250 iterations, each involving external calls to EigenLayer strategy contracts. At ~5,000 gas per external call, this alone exceeds 11M gas — approaching or exceeding the Ethereum block gas limit of ~30M when combined with the rest of the function's overhead. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```
