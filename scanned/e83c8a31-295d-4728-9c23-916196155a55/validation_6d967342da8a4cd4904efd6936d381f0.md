### Title
NodeDelegator Removal DoS via Dust Token Transfer Blocks Queue Management - (File: `contracts/LRTDepositPool.sol`)

### Summary
The `removeNodeDelegatorContractFromQueue()` function in `LRTDepositPool.sol` checks raw ERC20 `balanceOf` and native ETH balance of the NodeDelegator before allowing its removal. Any unprivileged user can permanently block this removal by transferring a dust amount of a supported LST token (or ETH) directly to the NodeDelegator contract, exceeding the `maxNegligibleAmount` threshold. When the queue is at capacity (`maxNodeDelegatorLimit = 10`), this prevents the admin from ever adding a new NodeDelegator.

### Finding Description

`_removeNodeDelegatorContractFromQueue()` performs two residue balance checks before removing a NodeDelegator:

```solidity
// contracts/LRTDepositPool.sol L584-587
_checkResidueEthBalance(nodeDelegatorAddress);
_checkResidueLSTBalance(nodeDelegatorAddress);
```

`_checkResidueEthBalance` reverts if:
```solidity
// contracts/LRTDepositPool.sol L617-623
address(nodeDelegatorAddress).balance > maxNegligibleAmount
```

`_checkResidueLSTBalance` reverts if:
```solidity
// contracts/LRTDepositPool.sol L638-643
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);
if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

The `IERC20(...).balanceOf(nodeDelegatorAddress)` component is a raw on-chain balance that any user can inflate by directly transferring tokens to the NodeDelegator address. The `maxNegligibleAmount` variable defaults to `0` (it is declared but never initialized in `initialize()`):

```solidity
// contracts/LRTDepositPool.sol L36
uint256 public maxNegligibleAmount;
```

Even if the admin sets `maxNegligibleAmount` to a non-zero value via `setMaxNegligibleAmount()`, an attacker can always transfer `maxNegligibleAmount + 1` wei of stETH or ETHx to the NodeDelegator, re-triggering the revert. The protocol supports a maximum of 10 NodeDelegators:

```solidity
// contracts/LRTDepositPool.sol L49
maxNodeDelegatorLimit = 10;
```

If all 10 slots are occupied and one NodeDelegator is blocked from removal, `addNodeDelegatorContractToQueue()` will revert with `MaximumNodeDelegatorLimitReached`, permanently preventing queue rotation.

### Impact Explanation

**Medium — Temporary/permanent freezing of protocol management with indirect fund impact.**

When the NodeDelegator queue is full (10 NDCs), a blocked removal prevents the admin from adding replacement NodeDelegators. If a NodeDelegator becomes insolvent, is compromised, or needs to be rotated out for operational reasons, the admin is unable to do so. User funds routed through that NodeDelegator into EigenLayer strategies remain locked in an unmanageable state. The attacker's cost is negligible (1 wei of stETH or ETHx).

### Likelihood Explanation

**Medium.** The attack requires no special privileges — any holder of a supported LST (stETH, ETHx) can execute it. The cost is 1 wei. The attack is persistent: even after the admin raises `maxNegligibleAmount`, the attacker can re-execute with a slightly larger amount. The attack is most impactful when the queue is at capacity, which is a normal operational state for a mature protocol.

### Recommendation

1. **Do not rely on raw `balanceOf` for removal guards.** Track internal accounting of assets deposited into the NodeDelegator rather than using `balanceOf`, which is externally manipulable.
2. **Add an admin rescue function** on the NodeDelegator that allows sweeping arbitrary ERC20 dust to the treasury, so the admin can clear the balance before calling removal.
3. **Alternatively**, change the removal check to use a strict internal accounting variable (e.g., `totalManagedAssets`) rather than `IERC20(asset).balanceOf(nodeDelegatorAddress)`, so direct transfers do not affect the guard.

### Proof of Concept

1. Protocol has 10 NodeDelegators registered (queue at capacity).
2. Admin decides to remove NDC at index 0 (e.g., it is being deprecated).
3. Attacker calls `stETH.transfer(nodeDelegatorQueue[0], 1)` — costs 1 wei of stETH.
4. Admin calls `removeNodeDelegatorContractFromQueue(nodeDelegatorQueue[0])`.
5. `_checkResidueLSTBalance` computes `IERC20(stETH).balanceOf(ndc) = 1 > maxNegligibleAmount (= 0)` and reverts with `NodeDelegatorHasAssetBalance`.
6. Admin raises `maxNegligibleAmount` to `100`. Attacker transfers `101` wei of stETH to the NDC. Step 5 repeats.
7. Admin can never remove the NDC. Queue remains full. No new NodeDelegators can be added.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L36-36)
```text
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
```

**File:** contracts/LRTDepositPool.sol (L328-330)
```text
    function removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) external onlyLRTAdmin {
        _removeNodeDelegatorContractFromQueue(nodeDelegatorAddress);
    }
```

**File:** contracts/LRTDepositPool.sol (L579-597)
```text
    function _removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) internal {
        // 1. check if node delegator contract is in queue and find Index
        uint256 ndcIndex = _getNDCIndex(nodeDelegatorAddress);

        // 2. revert if node delegator contract has any asset balances.
        // 2.1 check if NDC has native ETH balance in eigen layer or/and in itself.
        _checkResidueEthBalance(nodeDelegatorAddress);
        // 2.2  check if NDC has LST balance
        _checkResidueLSTBalance(nodeDelegatorAddress);

        // 3. remove node delegator contract from queue
        // 3.1 remove from isNodeDelegator mapping
        isNodeDelegator[nodeDelegatorAddress] = 0;
        // 3.2 remove from nodeDelegatorQueue
        nodeDelegatorQueue[ndcIndex] = nodeDelegatorQueue[nodeDelegatorQueue.length - 1];
        nodeDelegatorQueue.pop();

        emit NodeDelegatorRemovedFromQueue(nodeDelegatorAddress);
    }
```

**File:** contracts/LRTDepositPool.sol (L615-645)
```text
    /// @dev reverts if NDC has native ETH balance in eigen layer or in itself.
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }

    /// @dev reverts if NDC has LST balance
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
```
