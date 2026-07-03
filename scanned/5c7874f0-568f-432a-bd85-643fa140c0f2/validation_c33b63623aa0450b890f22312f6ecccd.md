### Title
Unbounded Nested Loop in `NodeDelegator.getAssetUnstaking()` Causes Permanent Revert of Deposits and Oracle Updates - (File: contracts/NodeDelegator.sol)

---

### Summary

`NodeDelegator.getAssetUnstaking()` fetches all queued EigenLayer withdrawals via `getQueuedWithdrawals()` and iterates over them with a nested loop that makes external calls per iteration. This function is invoked for every NDC on every user deposit and every oracle price update. As the number of pending withdrawals grows, gas consumption grows proportionally and will eventually exceed the block gas limit, permanently bricking deposits and oracle updates.

---

### Finding Description

`NodeDelegator.getAssetUnstaking()` contains a nested loop over all queued withdrawals returned by EigenLayer's `DelegationManager.getQueuedWithdrawals()`:

```solidity
// contracts/NodeDelegator.sol lines 405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));

    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            IStrategy strategy = withdrawal.strategies[strategyIndex];

            address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                ? LRTConstants.ETH_TOKEN
                : address(strategy.underlyingToken());   // external call

            if (strategyAsset != asset) continue;

            uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
            amount += strategyAsset == LRTConstants.ETH_TOKEN
                ? sharesToUnstake
                : strategy.sharesToUnderlyingView(sharesToUnstake);  // external call
        }
    }
}
``` [1](#0-0) 

This function is called from `getETHDistributionData()` and `getAssetDistributionData()` for **every NDC** in `nodeDelegatorQueue`:

```solidity
// contracts/LRTDepositPool.sol lines 484-492
for (uint256 i; i < ndcsCount;) {
    ethLyingInNDCs += nodeDelegatorQueue[i].balance;
    ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
    ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
        .getAssetUnstaking(LRTConstants.ETH_TOKEN);
    ...
}
``` [2](#0-1) 

`getETHDistributionData()` is called by `getTotalAssetDeposits()`, which is called by `_checkIfDepositAmountExceedesCurrentLimit()`, which is called by `_beforeDeposit()` on every `depositETH()` and `depositAsset()` invocation: [3](#0-2) 

The same chain is triggered by `LRTOracle._getTotalEthInProtocol()` → `getTotalAssetDeposits()` → `getETHDistributionData()` → `getAssetUnstaking()` for each NDC, meaning `updateRSETHPrice()` is also affected: [4](#0-3) 

The total gas scales as: `ndcCount × queuedWithdrawalsPerNDC × strategiesPerWithdrawal × externalCallCost`. Each call to `initiateUnstaking()` or `undelegate()` adds entries to the queue. No pagination exists.

---

### Impact Explanation

Once the cumulative gas for iterating all queued withdrawals across all NDCs exceeds the block gas limit (~30M gas on Ethereum mainnet), every call to `depositETH()`, `depositAsset()`, and `updateRSETHPrice()` will revert. This permanently freezes new deposits and prevents oracle price updates, which in turn blocks the withdrawal unlock flow (`unlockQueue` depends on `rsETHPrice`). This constitutes **temporary (and eventually permanent) freezing of funds** and **unbounded gas consumption**.

---

### Likelihood Explanation

The protocol actively uses `initiateUnstaking()` and `undelegate()` as part of normal operations. Each `initiateUnstaking()` call adds one withdrawal entry; `undelegate()` adds one entry per strategy. With multiple NDCs and multiple strategies each, the queue grows with normal protocol activity. No mechanism removes completed withdrawals from the view returned by `getQueuedWithdrawals()` until `completeUnstaking()` is called, and the `maxUncompletedWithdrawalCount` cap is an admin-set value that may be set high. This is a realistic, time-delayed failure mode.

---

### Recommendation

1. Add pagination parameters (`startIndex`, `endIndex`) to `getAssetUnstaking()` so callers can batch the computation.
2. Cache or snapshot the unstaking amount off-chain and update it incrementally rather than recomputing from the full withdrawal queue on every call.
3. Alternatively, maintain a running `assetUnstaking` counter in storage that is incremented on `initiateUnstaking()` and decremented on `completeUnstaking()`, eliminating the need to iterate the queue entirely.

---

### Proof of Concept

1. Deploy the protocol with 5 NDCs (`maxNodeDelegatorLimit = 10`).
2. For each NDC, call `initiateUnstaking()` repeatedly until `maxUncompletedWithdrawalCount` pending withdrawals exist per NDC.
3. Call `depositETH{value: 1 ether}(0, "")` as an unprivileged user.
4. The call chain `depositETH → _beforeDeposit → getTotalAssetDeposits → getETHDistributionData → getAssetUnstaking` (×5 NDCs) iterates all queued withdrawals with external calls per entry.
5. Observe the transaction reverts with out-of-gas once the total iterations exceed the gas budget.
6. No further deposits are possible; `updateRSETHPrice()` also reverts, blocking the withdrawal unlock flow.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L484-492)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
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
