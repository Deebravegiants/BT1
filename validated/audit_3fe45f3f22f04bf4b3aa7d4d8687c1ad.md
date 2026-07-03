### Title
Unbounded Gas Consumption in `updateRSETHPrice()` Due to Uncapped `supportedAssetList` — (File: contracts/LRTOracle.sol)

---

### Summary

`updateRSETHPrice()` is publicly callable with no access control. It iterates over the entire `supportedAssetList` with no enforced cap, making multiple external calls per asset (oracle price fetch + nested loop over all node delegators). As the protocol adds more supported assets, the gas cost grows without bound, eventually exceeding the block gas limit and permanently breaking the price oracle.

---

### Finding Description

`updateRSETHPrice()` in `LRTOracle.sol` is declared `public whenNotPaused` with no role restriction — any external caller can invoke it. [1](#0-0) 

It delegates to `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`. [2](#0-1) 

`_getTotalEthInProtocol()` fetches the full `supportedAssetList` from `LRTConfig` and iterates over every entry with no cap: [3](#0-2) 

For each asset it makes two expensive external calls:
1. `getAssetPrice(asset)` — an external oracle call.
2. `ILRTDepositPool.getTotalAssetDeposits(asset)` — which itself calls `getAssetDistributionData`, which loops over the entire `nodeDelegatorQueue` and for each node delegator calls `getAssetBalance` and `getAssetUnstaking`. [4](#0-3) 

`getAssetUnstaking` on each `NodeDelegator` fetches all queued EigenLayer withdrawals and iterates over their strategies: [5](#0-4) 

The root cause is that `_addNewSupportedAsset()` in `LRTConfig` enforces no cap on `supportedAssetList`: [6](#0-5) 

The total gas cost is therefore **O(supportedAssets × nodeDelegators × queuedWithdrawals)** — all three dimensions can grow over the protocol's lifetime with no hard ceiling on `supportedAssets`.

---

### Impact Explanation

If `supportedAssetList` grows large enough (combined with the nested per-asset loops), `updateRSETHPrice()` will exceed the block gas limit and become permanently uncallable. This freezes the rsETH price oracle: `rsETHPrice` can no longer be updated. Downstream effects include:

- `depositETH` / `depositAsset` compute `rsethAmountToMint` using the stale `rsETHPrice`, causing users to mint at an incorrect exchange rate — **contract fails to deliver promised returns**.
- `initiateWithdrawal` computes `expectedAssetAmount` using the stale price, causing incorrect withdrawal amounts.
- The `_updateRsETHPrice` fee-minting and price-protection logic (pause-on-drop) also becomes permanently disabled.

Impact: **Medium — Unbounded gas consumption / contract fails to deliver promised returns.**

---

### Likelihood Explanation

`TIME_LOCK_ROLE` can add new supported assets via `addNewSupportedAsset`. There is no cap. As the protocol expands to support more LSTs (a stated goal), the list grows organically. No attacker action is required — normal protocol operation is sufficient. The trigger (`updateRSETHPrice()`) is callable by any unprivileged address at any time.

Likelihood: **Low-Medium** (requires organic protocol growth, but no adversarial action).

---

### Recommendation

Enforce a maximum cap on `supportedAssetList` inside `_addNewSupportedAsset()` in `LRTConfig.sol`, analogous to how `maxNodeDelegatorLimit` caps `nodeDelegatorQueue` in `LRTDepositPool`:

```solidity
uint256 public maxSupportedAssets; // e.g., initialized to 20

function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    if (supportedAssetList.length >= maxSupportedAssets) {
        revert MaxSupportedAssetsReached();
    }
    // ... existing logic
}
```

This mirrors the fix recommended in the referenced BNB Chain PR: validate the size limit early, before any processing occurs.

---

### Proof of Concept

1. Protocol adds N supported assets via `TIME_LOCK_ROLE` (e.g., N = 50 LSTs, each with a node delegator and queued withdrawals).
2. Any unprivileged address calls `updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` iterates 50 times; each iteration calls `getAssetPrice` (external oracle) + `getTotalAssetDeposits` (which loops over all NDCs, each calling `getAssetUnstaking` which loops over all queued EigenLayer withdrawals).
4. Total gas exceeds the 30M block gas limit.
5. `updateRSETHPrice()` reverts on every call — the oracle is permanently frozen.
6. All subsequent deposits and withdrawals use the last stored `rsETHPrice`, which diverges from the true value over time.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
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
