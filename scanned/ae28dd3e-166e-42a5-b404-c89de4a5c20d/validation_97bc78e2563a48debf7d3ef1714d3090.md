### Title
Unbounded Nested-Loop Gas Consumption in `updateRSETHPrice()` Due to Missing Length Cap on `supportedAssetList` — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every entry in `supportedAssetList`. For each asset it calls `LRTDepositPool.getTotalAssetDeposits()`, which in turn iterates over every NDC in `nodeDelegatorQueue`, and for each NDC calls `NodeDelegator.getAssetUnstaking()`, which fetches and iterates over every pending EigenLayer queued-withdrawal. `LRTConfig.addNewSupportedAsset()` imposes no upper-bound on `supportedAssetList.length`, creating an unbounded nested loop whose gas cost grows as O(assets × NDCs × pending-withdrawals). When the product of those three dimensions is large enough, `updateRSETHPrice()` reverts on every call, permanently preventing price updates.

---

### Finding Description

**Call chain:**

```
updateRSETHPrice()          [public, no access control]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()          ← outer loop: supportedAssets.length
            └─ getTotalAssetDeposits(asset)
                 └─ getAssetDistributionData(asset)  ← middle loop: nodeDelegatorQueue.length
                      └─ getAssetUnstaking(asset)    ← inner loop: queuedWithdrawals.length
```

**Outer loop — no cap on `supportedAssetList`:**

`LRTConfig._addNewSupportedAsset()` pushes to `supportedAssetList` with no maximum-length guard:

```solidity
// LRTConfig.sol lines 106-118
function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    ...
    isSupportedAsset[asset] = true;
    supportedAssetList.push(asset);   // ← no length cap
    ...
}
```

`_getTotalEthInProtocol()` then iterates the full list:

```solidity
// LRTOracle.sol lines 333-348
address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
uint256 supportedAssetCount = supportedAssets.length;
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    ...
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    ...
}
```

**Middle loop — NDC queue:**

```solidity
// LRTDepositPool.sol lines 446-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
```

**Inner loop — unbounded EigenLayer queued withdrawals:**

```solidity
// NodeDelegator.sol lines 406-420
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, ...) =
    _getDelegationManager().getQueuedWithdrawals(address(this));

for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
        ...
    }
}
```

There is no cap on `queuedWithdrawals.length`. Pending EigenLayer withdrawals accumulate naturally as users request withdrawals and operators call `queueWithdrawal()`, and they are only removed when `completeQueuedWithdrawal()` is called. The inner loop is executed once per NDC per supported asset on every `updateRSETHPrice()` invocation.

---

### Impact Explanation

**Medium — Unbounded gas consumption / temporary freezing of unclaimed yield.**

`updateRSETHPrice()` is `public` with no access-control restriction beyond `whenNotPaused`. Once the combined loop depth exceeds the block gas limit, every call to `updateRSETHPrice()` reverts. Consequences:

1. The stored `rsETHPrice` becomes permanently stale — new depositors receive an incorrect rsETH mint amount.
2. The downside-protection mechanism (auto-pause on price drop) in `_updateRsETHPrice()` can never trigger, removing a critical safety rail.
3. The fee-minting path (`protocolFeeInETH`) is also blocked, freezing unclaimed protocol yield.

---

### Likelihood Explanation

**Medium.** The protocol is explicitly designed to onboard additional LST assets over time via `addNewSupportedAsset()`. Each new asset multiplies the per-call gas cost by the number of NDCs and their pending withdrawals. With even a modest number of supported assets (e.g., 10–15), a realistic NDC count (up to `maxNodeDelegatorLimit`, default 10), and a growing backlog of pending EigenLayer withdrawals (which accumulate during high withdrawal demand), the block gas limit becomes reachable without any adversarial action — purely through normal protocol growth.

---

### Recommendation

1. **Add a maximum-length guard in `_addNewSupportedAsset()`** analogous to `maxNodeDelegatorLimit`:
   ```solidity
   if (supportedAssetList.length >= maxSupportedAssetLimit) revert MaxSupportedAssetLimitReached();
   ```
2. **Cache or paginate `getAssetUnstaking()`** — instead of fetching all queued withdrawals on every price update, maintain a running accounting variable updated incrementally when withdrawals are queued and completed.
3. **Bound `maxNodeDelegatorLimit`** to a value that, combined with the maximum supported-asset count, keeps `updateRSETHPrice()` well within the block gas limit.

---

### Proof of Concept

1. Governance adds N supported assets via `LRTConfig.addNewSupportedAsset()` (no length cap enforced).
2. Operators queue M EigenLayer withdrawals across K NDCs via `NodeDelegator.queueWithdrawal()` (withdrawals accumulate without being completed).
3. Any external caller invokes `LRTOracle.updateRSETHPrice()`.
4. Execution enters `_getTotalEthInProtocol()` → N iterations → each calls `getTotalAssetDeposits()` → K NDC iterations → each calls `getAssetUnstaking()` → M withdrawal iterations.
5. Total iterations ≈ N × K × M. With N=10, K=10, M=50 the loop body (multiple SLOAD + external calls) easily exceeds 30 M gas, causing an out-of-gas revert.
6. `rsETHPrice` is never updated; the auto-pause safety mechanism is permanently disabled; protocol fee minting is frozen. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTConfig.sol (L106-118)
```text
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

**File:** contracts/NodeDelegator.sol (L405-420)
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

```
