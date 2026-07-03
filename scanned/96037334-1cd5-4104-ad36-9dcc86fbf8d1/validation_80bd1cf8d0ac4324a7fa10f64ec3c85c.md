### Title
Attacker Can Permanently Block `removeNodeDelegatorContractFromQueue()` by Sending ETH to NodeDelegator - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool._removeNodeDelegatorContractFromQueue()` checks that a `NodeDelegator`'s raw ETH balance does not exceed `maxNegligibleAmount` before allowing removal. Because `NodeDelegator` has an open `receive()` function, any attacker can send even 1 wei of ETH to the target `NodeDelegator` and cause the admin's removal transaction to revert indefinitely, at negligible cost.

### Finding Description

`_removeNodeDelegatorContractFromQueue()` calls `_checkResidueEthBalance()` before removing a NodeDelegator:

```solidity
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || address(nodeDelegatorAddress).balance > maxNegligibleAmount
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) {
        revert NodeDelegatorHasETH();
    }
}
``` [1](#0-0) 

The second condition, `address(nodeDelegatorAddress).balance > maxNegligibleAmount`, reads the raw ETH balance of the NodeDelegator contract. `maxNegligibleAmount` defaults to `0` (never explicitly initialized in `LRTDepositPool.initialize()`), meaning any non-zero ETH balance triggers the revert. [2](#0-1) 

`NodeDelegator` has an unrestricted `receive()` function that accepts ETH from any caller:

```solidity
receive() external payable {
    emit ETHReceived(msg.sender, msg.value);
}
``` [3](#0-2) 

An attacker can front-run any `removeNodeDelegatorContractFromQueue()` or `removeManyNodeDelegatorContractsFromQueue()` call by sending 1 wei of ETH to the target NodeDelegator, causing the admin's transaction to revert with `NodeDelegatorHasETH`. [4](#0-3) 

The same griefing vector applies to `_checkResidueLSTBalance()`, which checks `IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress) > maxNegligibleAmount`. An attacker can transfer any supported LST token directly to the NodeDelegator to trigger `NodeDelegatorHasAssetBalance`. [5](#0-4) 

The admin can attempt to drain the NodeDelegator's ETH via `transferBackToLRTDepositPool()`, but the attacker can front-run the subsequent removal call again, creating a permanent race condition. [6](#0-5) 

### Impact Explanation

The admin is permanently blocked from removing a NodeDelegator from the queue. This prevents:
- Emergency decommissioning of a compromised or misbehaving NodeDelegator
- Protocol restructuring (e.g., migrating to a new NodeDelegator)
- Reducing the `nodeDelegatorQueue` below `maxNodeDelegatorLimit` to add a replacement

While the admin can pause the NodeDelegator, they cannot remove it from the queue, which affects `getAssetDistributionData()`, `getTotalAssetDeposits()`, and all downstream accounting that iterates over `nodeDelegatorQueue`. This constitutes a **temporary (and potentially permanent) freezing of admin control** over the NodeDelegator lifecycle.

### Likelihood Explanation

The attack requires no special permissions, no capital at risk (1 wei of ETH is sufficient), and can be repeated indefinitely. Any unprivileged external account can execute it. The attacker only needs to monitor the mempool for admin removal transactions and front-run them.

### Recommendation

Replace the raw ETH balance check with a check that only considers protocol-tracked ETH (i.e., ETH staked via EigenLayer or explicitly transferred through protocol paths). Alternatively, allow the admin to force-remove a NodeDelegator if its raw ETH balance is below a configurable threshold that the admin can atomically set and remove in a single transaction, or use a two-step removal that first drains the NodeDelegator atomically before checking balances.

### Proof of Concept

1. Admin calls `removeNodeDelegatorContractFromQueue(ndcAddress)`.
2. Attacker front-runs by calling `ndcAddress.call{value: 1}("")` (or any ETH transfer to the NodeDelegator's `receive()`).
3. `_checkResidueEthBalance(ndcAddress)` evaluates `address(ndcAddress).balance > maxNegligibleAmount` → `1 > 0` → `true` → reverts with `NodeDelegatorHasETH`.
4. Admin's transaction reverts.
5. Admin drains ETH via `transferBackToLRTDepositPool(ETH_TOKEN, 1)`.
6. Attacker front-runs the next removal attempt again with another 1 wei transfer.
7. The cycle repeats indefinitely at negligible cost to the attacker.

### Citations

**File:** contracts/LRTDepositPool.sol (L29-36)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;

    /// @notice maximum amount that can be ignored
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTDepositPool.sol (L328-330)
```text
    function removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) external onlyLRTAdmin {
        _removeNodeDelegatorContractFromQueue(nodeDelegatorAddress);
    }
```

**File:** contracts/LRTDepositPool.sol (L616-624)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L627-646)
```text
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
    }
```

**File:** contracts/NodeDelegator.sol (L81-83)
```text
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```

**File:** contracts/NodeDelegator.sol (L467-488)
```text
    function transferBackToLRTDepositPool(
        address asset,
        uint256 amount
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlyAssetTransferRole
    {
        address lrtDepositPool = lrtConfig.depositPool();

        if (asset == LRTConstants.ETH_TOKEN) {
            ILRTDepositPool(lrtDepositPool).receiveFromNodeDelegator{ value: amount }();

            emit EthTransferred(lrtDepositPool, amount);
        } else {
            IERC20(asset).safeTransfer(lrtDepositPool, amount);

            emit AssetTransferred(asset, lrtDepositPool, amount);
        }
    }
```
