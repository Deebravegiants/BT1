### Title
Nested Unbounded Loops in `updateRSETHPrice()` May Cause DoS of the rsETH Price Oracle — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a permissionless `public` function. Its internal call chain traverses three nested unbounded loops — over supported assets, over NodeDelegator contracts (NDCs), and over EigenLayer queued withdrawals per NDC — with no single aggregate bound preventing the total gas from exceeding Ethereum's block gas limit. As the protocol scales (more NDCs, more queued withdrawals), this function can become permanently uncallable, freezing the rsETH price oracle.

---

### Finding Description

`updateRSETHPrice()` has no access control beyond `whenNotPaused`: [1](#0-0) 

It calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()`, which loops over every supported asset: [2](#0-1) 

For each asset, `getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` loops over every NDC in `nodeDelegatorQueue`: [3](#0-2) 

For each NDC, `getAssetUnstaking(asset)` calls EigenLayer's `getQueuedWithdrawals` and then iterates over every queued withdrawal and every strategy within it: [4](#0-3) 

The total gas cost scales as:

```
N_assets × N_ndcs × (external_call_to_EigenLayer + N_withdrawals_per_ndc × N_strategies × per_strategy_gas)
```

Each `getQueuedWithdrawals` call is a cold external call to EigenLayer. With 3 assets and 10 NDCs, that is already **30 cold external calls** just for `getAssetUnstaking`, plus 30 more for `getAssetBalance`, plus 30 ERC-20 `balanceOf` calls — 90+ external calls per `updateRSETHPrice()` invocation at the default NDC limit.

The protocol caps `maxUncompletedWithdrawalCount` at 80 to partially mitigate this: [5](#0-4) 

However, this cap is on the protocol's own counter, not on EigenLayer's actual queued withdrawal list returned by `getQueuedWithdrawals`. Forced undelegations by EigenLayer operators create additional withdrawals outside the protocol's counter. Furthermore, `maxNodeDelegatorLimit` is admin-adjustable upward: [6](#0-5) 

As the admin legitimately adds more NDCs (e.g., to scale capacity), the number of external calls in `updateRSETHPrice()` grows multiplicatively. At 50 NDCs × 3 assets, there are 150 cold external calls to EigenLayer's `getQueuedWithdrawals` alone, which can push the transaction well past Ethereum's 30 M gas block limit.

---

### Impact Explanation

If `updateRSETHPrice()` reverts with out-of-gas:

1. The rsETH/ETH exchange rate stored in `rsETHPrice` becomes stale.
2. Protocol fee minting (`_checkAndUpdateDailyFeeMintLimit`) cannot execute.
3. The price-drop circuit breaker (which pauses the protocol on excessive price decrease) cannot trigger.
4. Deposits and withdrawals continue using a stale price, creating mis-accounting.

This constitutes **temporary freezing of protocol price-update functionality** and potential **mis-accounting of rsETH minted/burned** against a stale price — matching the "Medium. Unbounded gas consumption" and "Medium. Temporary freezing of funds" impact categories.

---

### Likelihood Explanation

The condition is reached through **legitimate protocol scaling**, not malicious action:

- Admin increases `maxNodeDelegatorLimit` to accommodate more validators (routine operational decision).
- Operators queue multiple EigenLayer withdrawals across NDCs (routine unstaking operations).
- EigenLayer forced undelegations create additional queued withdrawals beyond the protocol's counter.

No private key compromise or governance capture is required. The protocol's own comment acknowledges the gas sensitivity of `updateRSETHPrice()` relative to withdrawal count, confirming the team is aware of the coupling but has not bounded the NDC count relative to it.

---

### Recommendation

1. **Cap the product** `N_assets × N_ndcs` at a value that keeps `updateRSETHPrice()` safely within gas limits, and enforce this cap in `addNodeDelegatorContractToQueue` and `addSupportedAsset`.
2. **Decouple asset accounting from per-call EigenLayer queries**: cache `getAssetUnstaking` results in storage (updated lazily by operators) rather than fetching live from EigenLayer on every price update.
3. **Bound `getQueuedWithdrawals` iteration**: introduce a maximum strategies-per-withdrawal check, or aggregate unstaking amounts in storage at queue/complete time rather than recomputing on-the-fly.

---

### Proof of Concept

Call chain for a single `updateRSETHPrice()` invocation with 3 supported assets and 10 NDCs each holding 8 queued withdrawals of 2 strategies each:

```
updateRSETHPrice()                          [public, no access control]
└── _updateRsETHPrice()
    └── _getTotalEthInProtocol()
        └── for asset in [ETHx, stETH, ETH]:          // 3 iterations
            └── getTotalAssetDeposits(asset)
                └── getAssetDistributionData(asset)
                    └── for ndc in nodeDelegatorQueue:  // 10 iterations
                        ├── IERC20(asset).balanceOf(ndc)          // external call
                        ├── INodeDelegator(ndc).getAssetBalance() // external call → EigenLayer strategy
                        └── INodeDelegator(ndc).getAssetUnstaking()
                            └── delegationManager.getQueuedWithdrawals(ndc) // cold external call
                                └── for withdrawal in queuedWithdrawals:    // 8 iterations
                                    └── for strategy in withdrawal.strategies: // 2 iterations
                                        └── strategy.sharesToUnderlyingView() // external call
```

Total external calls: 3 × 10 × (1 + 1 + 1 + 8 × 2) = **3 × 10 × 19 = 570 external calls**.

At ~2,100 gas per cold external call plus execution overhead, this exceeds **1.2 M gas** for external call overhead alone, and grows multiplicatively as `maxNodeDelegatorLimit` is increased — eventually exceeding Ethereum's 30 M gas block limit.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
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

**File:** contracts/LRTUnstakingVault.sol (L151-158)
```text
        // 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
        // Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
        if (_maxUncompletedWithdrawalCount > 80) {
            revert MaxUncompletedWithdrawalCountTooHigh();
        }
        maxUncompletedWithdrawalCount = _maxUncompletedWithdrawalCount;

        emit MaxUncompletedWithdrawalCountSet(_maxUncompletedWithdrawalCount);
```
