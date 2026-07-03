### Title
Anyone Can Permanently Block NodeDelegator Removal by Sending 1 Wei of a Supported LST - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkResidueLSTBalance` in `LRTDepositPool.sol` gates NodeDelegator removal on the raw ERC20 `balanceOf` of the NDC address. Because any external actor can transfer tokens directly to a NodeDelegator, an attacker can permanently block the admin from decommissioning any NDC by sending a dust amount of a supported LST to it.

### Finding Description
`_checkResidueLSTBalance` is called as part of `removeNodeDelegatorContractFromQueue` / `removeManyNodeDelegatorContractsFromQueue`. It iterates over all supported assets and computes:

```solidity
assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
    + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

if (assetBalance > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
``` [1](#0-0) 

The first term — `IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)` — is the raw on-chain ERC20 balance of the NDC contract. Standard ERC20 tokens allow any holder to transfer tokens to any address without the recipient's consent. Therefore, any unprivileged user can call `stETH.transfer(ndcAddress, 1)` (or any other supported LST) to make this balance non-zero.

The `maxNegligibleAmount` threshold is a global admin-controlled parameter. [2](#0-1)  If it is 0 (the default after initialization), even 1 wei blocks removal. If the admin raises it to `N`, the attacker simply sends `N + 1` wei. Because `maxNegligibleAmount` is global, raising it high enough to defeat the griefing simultaneously weakens the safety guarantee for all other NDCs — the admin faces an irresolvable dilemma.

The NodeDelegator's `receive()` function also accepts plain ETH, making `_checkResidueEthBalance`'s `address(nodeDelegatorAddress).balance > maxNegligibleAmount` check equally manipulable via a direct ETH send. [3](#0-2) 

### Impact Explanation
**Medium — Temporary (effectively permanent) freezing of funds / contract fails to deliver promised returns.**

The admin cannot decommission a NodeDelegator that has been drained of legitimate funds. Concretely:
- A compromised or malfunctioning NDC cannot be removed from `nodeDelegatorQueue`, keeping it in the active set used by `getTotalAssetDeposits` and operator routing logic.
- The 1-wei dust sent by the attacker is permanently stranded in the NDC because the removal precondition can never be satisfied while the attacker keeps front-running.
- The only escape — raising `maxNegligibleAmount` to `type(uint256).max` — disables the safety check globally, creating a separate risk.

### Likelihood Explanation
**High.** The attack requires only a standard ERC20 `transfer` call with 1 wei of any supported LST (stETH, cbETH, etc.). No special permissions, no flash loans, no complex setup. The attacker can monitor the mempool and front-run every removal attempt at negligible cost.

### Recommendation
Replace the raw `balanceOf` check with a tracked internal accounting variable that only increases when tokens enter the NDC through protocol-controlled paths (e.g., `transferAssetToNodeDelegator`). Alternatively, add a privileged `forceRemoveNodeDelegator` path that bypasses the balance check and sweeps any residual dust to a recovery address in the same transaction, removing the griefing surface entirely.

### Proof of Concept
1. Admin drains NDC1: all EigenLayer withdrawals complete, all LSTs transferred back to the deposit pool. `stETH.balanceOf(NDC1) == 0`, `getAssetBalance(NDC1) == 0`.
2. Admin submits `removeNodeDelegatorContractFromQueue(NDC1)`.
3. Attacker observes the pending transaction and front-runs with `stETH.transfer(NDC1, 1)`.
4. `_checkResidueLSTBalance` evaluates: `balanceOf(NDC1) = 1 > maxNegligibleAmount (= 0)` → reverts with `NodeDelegatorHasAssetBalance`.
5. Admin raises `maxNegligibleAmount` to `1` and retries.
6. Attacker front-runs again with `stETH.transfer(NDC1, 2)` → reverts again.
7. This loop continues indefinitely; NDC1 can never be removed from the queue. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTDepositPool.sol (L274-277)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
    }
```

**File:** contracts/LRTDepositPool.sol (L326-330)
```text
    /// @dev only callable by LRT admin
    /// @param nodeDelegatorAddress NodeDelegator contract address
    function removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) external onlyLRTAdmin {
        _removeNodeDelegatorContractFromQueue(nodeDelegatorAddress);
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
