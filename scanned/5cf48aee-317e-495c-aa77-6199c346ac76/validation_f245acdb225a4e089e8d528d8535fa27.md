Looking at the two key functions in `LRTUnstakingVault.sol`:

**`transferAssetToNodeDelegator` (lines 112–126):** [1](#0-0) 

There is no check against `queuedWithdrawalsBuffer[asset]`. The function transfers the full requested `amount` unconditionally.

**`getAssetsAvailableForInstantWithdrawal` (lines 229–238):** [2](#0-1) 

**`instantWithdrawal` guard in `LRTWithdrawalManager` (lines 231–233):** [3](#0-2) 

The invariant the buffer is supposed to enforce — that `vaultBalance >= queuedWithdrawalsBuffer[asset]` at all times — is **not enforced** by `transferAssetToNodeDelegator` or `transferETHToNodeDelegator`. Both functions simply transfer without checking the remaining balance against the buffer.

---

### Title
Missing buffer guard in `transferAssetToNodeDelegator` / `transferETHToNodeDelegator` allows draining vault below `queuedWithdrawalsBuffer`, breaking instant withdrawal availability — (`contracts/LRTUnstakingVault.sol`)

### Summary
`LRTUnstakingVault` maintains `queuedWithdrawalsBuffer[asset]` to partition vault liquidity: funds above the buffer are available for instant withdrawals; funds at or below the buffer are reserved for queued withdrawals. However, `transferAssetToNodeDelegator` and `transferETHToNodeDelegator` perform no check against this buffer, allowing an `ASSET_TRANSFER_ROLE` holder to move assets to a node delegator even when doing so reduces the vault balance below the buffer. After such a transfer, `getAssetsAvailableForInstantWithdrawal` returns 0, and any subsequent `instantWithdrawal` call in `LRTWithdrawalManager` reverts with `CantInstantWithdrawMoreThanAvailable`, despite the protocol having advertised positive availability.

### Finding Description
`transferAssetToNodeDelegator`: [1](#0-0) 

`transferETHToNodeDelegator`: [4](#0-3) 

Neither function reads `queuedWithdrawalsBuffer[asset]` or enforces that `balanceOf(asset) - amount >= queuedWithdrawalsBuffer[asset]` after the transfer. The buffer is set separately via `setQueuedWithdrawalsBuffer` (callable by `onlyLRTOperator`), but the transfer functions (callable by `onlyAssetTransferRole`) are entirely unaware of it.

`getAssetsAvailableForInstantWithdrawal` computes availability purely from the live balance: [5](#0-4) 

Once the balance is driven below the buffer, this returns 0, and `instantWithdrawal` reverts: [3](#0-2) 

### Impact Explanation
Instant withdrawal users are denied service — their calls revert — even though the protocol's own view function previously reported positive availability. No funds are lost (they are in the node delegator), but the contract fails to deliver the promised instant-withdrawal return path. This matches the **Low** scope: *Contract fails to deliver promised returns, but doesn't lose value.*

### Likelihood Explanation
Requires the `ASSET_TRANSFER_ROLE` holder to transfer an amount that exceeds `vaultBalance - queuedWithdrawalsBuffer[asset]`. This can happen accidentally (operator does not account for the buffer when sizing a transfer) or deliberately. The roles are distinct (`ASSET_TRANSFER_ROLE` vs `LRT_OPERATOR_ROLE` that sets the buffer), so the operator setting the buffer may not be the same entity executing the transfer, increasing the chance of an accidental violation.

### Recommendation
Add a post-transfer invariant check in both `transferAssetToNodeDelegator` and `transferETHToNodeDelegator`:

```solidity
uint256 remaining = balanceOf(asset);
if (remaining < queuedWithdrawalsBuffer[asset]) {
    revert TransferWouldViolateBuffer();
}
```

Alternatively, compute the maximum transferable amount before the transfer and revert if `amount` exceeds it.

### Proof of Concept

```
State:
  queuedWithdrawalsBuffer[TOKEN] = 100e18
  vault.balanceOf(TOKEN)         = 100e18 + 1e18   // buffer + epsilon

Step 1 (view):
  vault.getAssetsAvailableForInstantWithdrawal(TOKEN)
  → returns 1e18  (positive, instant withdrawal advertised as available)

Step 2 (operator tx):
  vault.transferAssetToNodeDelegator(0, TOKEN, 1e18 + 1)
  → succeeds (no buffer check), vault balance becomes 99999...999 < 100e18

Step 3 (view):
  vault.getAssetsAvailableForInstantWithdrawal(TOKEN)
  → reservedBuffer (100e18) >= vaultBalance (99.999...e18) → returns 0

Step 4 (user tx):
  withdrawalManager.instantWithdrawal(TOKEN, rsETHAmount, "")
  → assetAmountUnlocked > 0 > getAssetsAvailableForInstantWithdrawal(TOKEN)
  → reverts CantInstantWithdrawMoreThanAvailable

Assert: getAssetsAvailableForInstantWithdrawal == 0 after step 2,
        instantWithdrawal reverts in step 4.
        No funds lost; instant withdrawal path broken.
```

### Citations

**File:** contracts/LRTUnstakingVault.sol (L112-126)
```text
    function transferAssetToNodeDelegator(
        uint256 ndcIndex,
        address asset,
        uint256 amount
    )
        external
        nonReentrant
        onlyAssetTransferRole
        onlySupportedAsset(asset)
    {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.depositPool());
        address[] memory nodeDelegatorQueue = lrtDepositPool.getNodeDelegatorQueue();
        address nodeDelegator = nodeDelegatorQueue[ndcIndex];
        IERC20(asset).safeTransfer(nodeDelegator, amount);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L132-146)
```text
    function transferETHToNodeDelegator(
        uint256 ndcIndex,
        uint256 amount
    )
        external
        nonReentrant
        onlyAssetTransferRole
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.depositPool());
        address[] memory nodeDelegatorQueue = lrtDepositPool.getNodeDelegatorQueue();
        address nodeDelegator = nodeDelegatorQueue[ndcIndex];
        INodeDelegator(nodeDelegator).sendETHFromUnstakingVaultToNDC{ value: amount }();
        emit EthTransferred(nodeDelegator, amount);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L229-238)
```text
    function getAssetsAvailableForInstantWithdrawal(address asset)
        external
        view
        onlySupportedAsset(asset)
        returns (uint256 availableAmount)
    {
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L231-233)
```text
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }
```
