### Title
Unbounded Nested Gas Loop in `LRTOracle._getTotalEthInProtocol()` Can Permanently Block Price Updates — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a publicly callable function with no access control. It internally calls `_getTotalEthInProtocol()`, which iterates over the `supportedAssets` array — an array with **no enforced cap** — and for each asset calls `LRTDepositPool.getTotalAssetDeposits()`, which itself loops over `nodeDelegatorQueue`. As the protocol adds more supported assets through normal governance, this nested loop grows in gas cost. If it exceeds the block gas limit, `updateRSETHPrice()` becomes permanently uncallable, freezing the rsETH price and breaking the protocol's fee-accrual and price-protection mechanisms.

---

### Finding Description

`LRTOracle._getTotalEthInProtocol()` contains a nested loop structure:

1. **Outer loop** — iterates over every entry in `supportedAssets` (fetched from `LRTConfig.getSupportedAssetList()`). There is no cap on this array; `LRTConfig.addNewSupportedAsset()` is callable by `TIME_LOCK_ROLE` with no upper bound check.

2. **Inner loop** — for each asset, calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)`, which loops over every entry in `nodeDelegatorQueue` (bounded by `maxNodeDelegatorLimit`, default 10, admin-settable).

3. **Innermost call** — for each NDC in the queue, calls `INodeDelegator.getAssetUnstaking(asset)`, which calls EigenLayer's `getQueuedWithdrawals()` and iterates over all queued withdrawal structs and their strategy arrays.

The combined gas cost is `O(supportedAssets × nodeDelegatorQueue × queuedWithdrawals × strategies)`. The outer dimension has no cap.

`updateRSETHPrice()` is the entry point:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

It has no role restriction — any address can call it. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()` unconditionally.

---

### Impact Explanation

If `_getTotalEthInProtocol()` runs out of gas, every call to `updateRSETHPrice()` (and `updateRSETHPriceAsManager()`) reverts. Consequences:

- **Stale rsETH price**: `rsETHPrice` is never updated. All subsequent deposits via `depositETH()`/`depositAsset()` and withdrawals via `initiateWithdrawal()` use the frozen price, causing incorrect rsETH minting and incorrect asset-out calculations.
- **Fee accrual halted**: Protocol fees are minted inside `_updateRsETHPrice()`. A permanently broken update loop means no fees are ever collected.
- **Downside protection disabled**: The automatic pause triggered when `newRsETHPrice < highestRsethPrice` beyond the threshold can never fire, removing a critical safety mechanism.
- **`updateRSETHPriceAsManager()` also broken**: The manager override path calls the same `_updateRsETHPrice()` and is equally affected.

Impact classification: **Medium — Unbounded gas consumption** (and secondary: permanent freezing of yield/fee accrual).

---

### Likelihood Explanation

The `supportedAssets` array grows through normal governance (`TIME_LOCK_ROLE` calling `addNewSupportedAsset()`). No malicious actor is required. As the protocol expands to support additional LSTs (e.g., rETH, cbETH, sfrxETH, osETH, etc.) and increases `maxNodeDelegatorLimit` to accommodate more validators, the nested loop cost grows multiplicatively. With 10 assets, 10 NDCs, and 10 queued withdrawals per NDC, the loop already executes ~1,000 external calls. At 20 assets and 20 NDCs, it is ~4,000 calls — well within range of hitting the 30M gas block limit given each `getAssetUnstaking` call involves EigenLayer storage reads.

---

### Recommendation

1. **Cap `supportedAssets`**: Add a `maxSupportedAssets` limit in `LRTConfig.addNewSupportedAsset()`, analogous to `maxNodeDelegatorLimit` in `LRTDepositPool`.
2. **Cache or snapshot TVL**: Instead of recomputing the full nested loop on every `updateRSETHPrice()` call, maintain a running TVL accumulator updated incrementally on deposit/withdrawal events.
3. **Separate price update from TVL computation**: Allow `_getTotalEthInProtocol()` to be called in batches (per-asset) and aggregate results, so no single transaction must traverse the entire array.

---

### Proof of Concept

**Entry path (no privilege required):**

```
anyone → LRTOracle.updateRSETHPrice()          [public, whenNotPaused]
           └─ _updateRsETHPrice()
                └─ _getTotalEthInProtocol()
                     └─ for each asset in supportedAssets:          ← UNBOUNDED
                          └─ LRTDepositPool.getTotalAssetDeposits(asset)
                               └─ getAssetDistributionData(asset)
                                    └─ for each NDC in nodeDelegatorQueue:
                                         └─ INodeDelegator.getAssetUnstaking(asset)
                                              └─ DelegationManager.getQueuedWithdrawals()
                                                   └─ for each withdrawal × strategy
```

**Root cause lines:** [1](#0-0) [2](#0-1) 

`supportedAssets` has no cap: [3](#0-2) 

Inner loop over `nodeDelegatorQueue` per asset: [4](#0-3) 

Innermost nested loop in `getAssetUnstaking`: [5](#0-4)

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

**File:** contracts/LRTConfig.sol (L99-118)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }

    /// @dev private function to add a new supported asset
    /// @param asset Asset address
    /// @param depositLimit Deposit limit for the asset
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
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
