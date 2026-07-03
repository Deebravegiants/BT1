### Title
Attacker Can Permanently Block `removeNodeDelegatorContractFromQueue` via Dust Token Transfer - (File: contracts/LRTDepositPool.sol)

---

### Summary

`_removeNodeDelegatorContractFromQueue` in `LRTDepositPool` checks that a `NodeDelegator` holds no residual ETH or LST balance before allowing its removal. Because `NodeDelegator` has an open `receive()` function and ERC20 tokens can be freely transferred to any address, an unprivileged attacker can front-run the admin's removal transaction by sending as little as 1 wei of ETH or 1 wei of a supported LST token directly to the `NodeDelegator`. This causes the balance check to exceed `maxNegligibleAmount`, reverting the admin's transaction. The attacker can repeat this indefinitely at negligible cost, permanently blocking the admin from decommissioning any `NodeDelegator`.

---

### Finding Description

`removeNodeDelegatorContractFromQueue` (and its batch variant `removeManyNodeDelegatorContractsFromQueue`) delegate to `_removeNodeDelegatorContractFromQueue`, which enforces two balance guards before removing the NDC:

```solidity
// contracts/LRTDepositPool.sol
function _removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) internal {
    uint256 ndcIndex = _getNDCIndex(nodeDelegatorAddress);
    _checkResidueEthBalance(nodeDelegatorAddress);   // ← guard 1
    _checkResidueLSTBalance(nodeDelegatorAddress);   // ← guard 2
    ...
}
```

**Guard 1 – ETH balance check:**

```solidity
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || address(nodeDelegatorAddress).balance > maxNegligibleAmount   // ← manipulable
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) {
        revert NodeDelegatorHasETH();
    }
}
```

`NodeDelegator` has an unrestricted `receive()` function:

```solidity
// contracts/NodeDelegator.sol
receive() external payable {
    emit ETHReceived(msg.sender, msg.value);
}
```

Any caller can send ETH directly to the NDC, inflating `address(nodeDelegatorAddress).balance` above `maxNegligibleAmount`.

**Guard 2 – LST balance check:**

```solidity
function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
    ...
    assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)   // ← manipulable
        + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
    assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

    if (assetBalance > maxNegligibleAmount) {
        revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
    }
}
```

Any caller can `transfer` a supported LST token directly to the NDC address, inflating `IERC20(...).balanceOf(nodeDelegatorAddress)` above `maxNegligibleAmount`.

---

### Impact Explanation

An attacker can permanently prevent the admin from removing any `NodeDelegator` from the queue. Consequences include:

- **NDC slot exhaustion:** If `nodeDelegatorQueue.length` reaches `maxNodeDelegatorLimit`, no new NDCs can be added, blocking protocol expansion or replacement of compromised NDCs.
- **Inability to decommission:** A deprecated or misbehaving NDC cannot be formally removed, leaving it in the active queue indefinitely.
- **Operational freeze:** The admin cannot restructure the NDC set in response to changing conditions.

This maps to **Medium – Temporary (indefinitely renewable) freezing of admin operations / unclaimed yield**.

---

### Likelihood Explanation

- **Cost:** 1 wei of ETH or 1 wei of any supported LST token is sufficient.
- **Repeatability:** The attacker can re-execute the front-run every time the admin retries, at negligible cost.
- **No special permissions required:** Any externally owned account can call `transfer` on an ERC20 or send ETH via `call`.
- **Realistic scenario:** Any actor who benefits from keeping a specific NDC in the queue (e.g., a competing protocol, a griever) has clear motivation.

---

### Recommendation

1. **Remove the balance check from the removal path.** Instead of blocking removal when residual balance exists, allow removal and let the admin sweep residual tokens separately (e.g., via `transferBackToLRTDepositPool`).
2. **Alternatively, use a stored accounting variable** (not `balanceOf`) to track the NDC's managed balance, so externally donated tokens do not affect the guard.
3. **Restrict the `receive()` function** on `NodeDelegator` to only accept ETH from known protocol addresses (deposit pool, unstaking vault, EigenLayer pod), preventing arbitrary ETH donations.

---

### Proof of Concept

1. Admin calls `removeNodeDelegatorContractFromQueue(ndcAddress)` to decommission a NodeDelegator.
2. Attacker observes the pending transaction in the mempool.
3. Attacker front-runs with:
   ```solidity
   // Option A: ETH donation (1 wei is enough if maxNegligibleAmount == 0)
   (bool ok,) = ndcAddress.call{value: 1}("");
   // Option B: LST token donation
   IERC20(stETH).transfer(ndcAddress, 1);
   ```
4. `_checkResidueEthBalance` or `_checkResidueLSTBalance` now sees `balance > maxNegligibleAmount` and reverts with `NodeDelegatorHasETH` or `NodeDelegatorHasAssetBalance`.
5. Admin's transaction reverts. Attacker repeats on every retry.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** contracts/NodeDelegator.sol (L79-83)
```text
    /// @dev due to a bit heavy logic, eth transfer using `transfer()` and `send()` will fail
    /// @dev hence please use `call()` to send eth to this contract
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```
