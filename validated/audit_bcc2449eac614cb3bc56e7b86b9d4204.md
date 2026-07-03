### Title
Attacker Can Permanently Block NodeDelegator Removal via Direct Token/ETH Transfer - (File: `contracts/LRTDepositPool.sol`)

### Summary
The `_checkResidueLSTBalance` and `_checkResidueEthBalance` functions in `LRTDepositPool` gate NodeDelegator removal on raw `balanceOf` / `address.balance` reads. Because `NodeDelegator` has an open `receive()` function and ERC-20 tokens can always be transferred to any address, an unprivileged attacker can permanently prevent the admin from removing any NodeDelegator from the queue by donating a trivial amount of a supported asset.

### Finding Description
`removeNodeDelegatorContractFromQueue` (and its batch variant) calls `_removeNodeDelegatorContractFromQueue`, which in turn calls two balance-gate helpers before allowing removal:

```solidity
// contracts/LRTDepositPool.sol L616-L623
function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
    if (
        INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
            || address(nodeDelegatorAddress).balance > maxNegligibleAmount   // ← raw ETH balance
            || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
    ) {
        revert NodeDelegatorHasETH();
    }
}
```

```solidity
// contracts/LRTDepositPool.sol L627-L645
function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
    ...
    assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)   // ← raw ERC-20 balance
                 + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
    assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

    if (assetBalance > maxNegligibleAmount) {
        revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
    }
}
```

`NodeDelegator` exposes an unrestricted `receive()`:

```solidity
// contracts/NodeDelegator.sol L81-L83
receive() external payable {
    emit ETHReceived(msg.sender, msg.value);
}
```

An attacker can:
1. Send `maxNegligibleAmount + 1` wei of ETH directly to the NodeDelegator → `address(nodeDelegatorAddress).balance > maxNegligibleAmount` → `_checkResidueEthBalance` reverts with `NodeDelegatorHasETH`.
2. Send `maxNegligibleAmount + 1` wei of any supported LST directly to the NodeDelegator → `IERC20(asset).balanceOf(nodeDelegatorAddress)` exceeds the threshold → `_checkResidueLSTBalance` reverts with `NodeDelegatorHasAssetBalance`.

Either path permanently blocks `removeNodeDelegatorContractFromQueue` for that NDC, because the raw balance can never be reduced by the admin through any protocol-provided function (there is no "sweep dust" path for the NDC itself).

The structural parallel to the reported bug is exact: a balance read that includes tokens freely transferable by anyone is used as a hard gate on a critical protocol operation.

### Impact Explanation
The admin loses the ability to remove a NodeDelegator from the queue. If that NDC must be decommissioned (e.g., its EigenLayer operator is slashed, the NDC is compromised, or the protocol needs to restructure its delegation topology), the removal is permanently blocked. Assets delegated through that NDC remain locked in the EigenLayer strategy with no path to migrate them to a replacement NDC, constituting a temporary-to-permanent freeze of the restaked funds routed through that delegator.

**Impact:** Low — contract fails to deliver promised administrative returns; in a worst-case decommission scenario escalates toward temporary fund freeze.

### Likelihood Explanation
The attack requires no privilege, no flash loan, and no coordination. Sending 1 wei of ETH or a supported LST to a NodeDolgator address costs only gas. The attacker can monitor the mempool for `removeNodeDelegatorContractFromQueue` calls and front-run them, or pre-emptively grief any NDC at any time. Cost to the attacker is negligible; the effect is permanent until the protocol deploys a new contract version.

### Recommendation
Replace raw `balanceOf` / `address.balance` reads with an internal accounting variable that is only updated through controlled protocol entry points (deposits, withdrawals, transfers via role-gated functions). Alternatively, add a role-gated `sweepDust(address ndc, address asset, uint256 amount)` function that allows the admin to drain any residual balance from an NDC before removal, analogous to the remediation suggested in the reference report (clearing idle assets before checking the zero condition).

### Proof of Concept
1. Protocol has NodeDelegator `NDC_A` with zero EigenLayer shares and zero queued withdrawals — legitimately removable.
2. Attacker calls `NDC_A.transfer{value: maxNegligibleAmount + 1}()` (or `IERC20(stETH).transfer(NDC_A, maxNegligibleAmount + 1)`).
3. Admin calls `LRTDepositPool.removeNodeDelegatorContractFromQueue(NDC_A)`.
4. `_checkResidueEthBalance` (or `_checkResidueLSTBalance`) reads the inflated balance and reverts.
5. `NDC_A` can never be removed; any assets that must be migrated away from it are frozen in place.

Relevant code: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L616-623)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
```

**File:** contracts/LRTDepositPool.sol (L627-645)
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
```

**File:** contracts/NodeDelegator.sol (L81-83)
```text
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```
