### Title
Attacker Can Grief `removeNodeDelegatorContractFromQueue()` by Sending ETH to NodeDelegator - (File: contracts/LRTDepositPool.sol)

### Summary
`_removeNodeDelegatorContractFromQueue()` in `LRTDepositPool.sol` enforces a residual-balance check before removing a NodeDelegator from the queue. Because `NodeDelegator` has an open `receive()` function, any unprivileged attacker can send ETH to a NodeDelegator to keep its balance above `maxNegligibleAmount`, permanently blocking the admin's removal call. The admin can drain the ETH via `transferBackToLRTDepositPool()`, but the attacker can front-run the subsequent removal attempt, repeating the block indefinitely at low cost.

### Finding Description
`removeNodeDelegatorContractFromQueue()` (admin-only) delegates to `_removeNodeDelegatorContractFromQueue()`, which calls `_checkResidueEthBalance()`:

```solidity
// LRTDepositPool.sol L616-L624
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || address(nodeDelegatorAddress).balance > maxNegligibleAmount   // ← attacker-controlled
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) {
        revert NodeDelegatorHasETH();
    }
}
```

`NodeDelegator` has an unrestricted `receive()`:

```solidity
// NodeDelegator.sol L81-L83
receive() external payable {
    emit ETHReceived(msg.sender, msg.value);
}
```

Any caller can send `maxNegligibleAmount + 1 wei` of ETH to the NodeDelegator, causing `_checkResidueEthBalance` to revert. The admin's only recourse is to call `transferBackToLRTDepositPool(ETH_TOKEN, amount)` (requires `onlyAssetTransferRole`) to drain the balance, then immediately call `removeNodeDelegatorContractFromQueue`. An attacker watching the mempool can front-run the removal call by re-sending ETH, repeating the block indefinitely.

The same pattern applies to supported LST tokens via `_checkResidueLSTBalance()`:

```solidity
// LRTDepositPool.sol L638-L643
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

An attacker holding any supported LST (stETH, ETHx, etc.) can ERC20-transfer a dust amount directly to the NodeDelegator address to trigger this revert.

### Impact Explanation
The admin (`onlyLRTAdmin`) cannot remove a NodeDelegator from `nodeDelegatorQueue`. This blocks decommissioning of a malfunctioning or compromised NodeDelegator, prevents queue slot reclamation, and can delay emergency protocol management. No user funds are directly stolen, but the contract fails to deliver its promised administrative capability. Severity: **Low — contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
The attack requires only sending ETH (or a dust amount of a supported LST) to the NodeDelegator address — no privileged access, no special tokens beyond what any DeFi user holds. The cost per grief cycle is `maxNegligibleAmount + 1 wei` of ETH (or equivalent LST). The attacker can sustain the block indefinitely at minimal cost by monitoring the mempool and front-running each removal attempt.

### Recommendation
- Separate the "balance check" from the "removal" step: allow the admin to force-remove a NodeDelegator that has been explicitly drained, using a two-step commit-reveal or a private-mempool (Flashbots) bundle that atomically drains and removes.
- Alternatively, replace the raw `address(ndc).balance` check with a tracked internal accounting variable (similar to how `stakedButUnverifiedNativeETH` is tracked), so that unilaterally sent ETH is not counted as protocol-owned balance.
- For LST tokens, use an internal deposit-tracking mapping rather than `IERC20.balanceOf()` to distinguish protocol-deposited tokens from externally sent dust.

### Proof of Concept
1. Admin intends to call `removeNodeDelegatorContractFromQueue(NDC)`.
2. Attacker sends `maxNegligibleAmount + 1 wei` ETH to `NDC` (accepted by `receive()`).
3. Admin's call reverts: `NodeDelegatorHasETH`.
4. Admin (Asset Transfer Role) calls `NDC.transferBackToLRTDepositPool(ETH_TOKEN, balance)` to drain ETH.
5. Attacker observes the drain tx in the mempool and front-runs the admin's next `removeNodeDelegatorContractFromQueue(NDC)` call by re-sending ETH.
6. Admin's removal reverts again — loop repeats at attacker's discretion. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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
