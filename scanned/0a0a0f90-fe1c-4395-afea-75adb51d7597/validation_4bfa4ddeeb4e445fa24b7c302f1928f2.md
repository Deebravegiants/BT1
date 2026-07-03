### Title
`stakedButUnverifiedNativeETH` Not Decremented When Validator Exits Before Credential Verification, Inflating Protocol TVL and rsETH Price - (File: `contracts/NodeDelegator.sol`)

### Summary
The `stakedButUnverifiedNativeETH` counter in `NodeDelegator` is incremented when 32 ETH is staked to a validator but is only ever decremented through `verifyWithdrawalCredentials()`. If a validator exits the beacon chain before its withdrawal credentials are verified — for example, because the credentials were incorrect and EigenLayer rejects the proof — the counter is never decremented. No invalidation or "alienation" path exists to correct it. This permanently inflates `getEffectivePodShares()`, which propagates into the protocol TVL and rsETH price calculation, causing the protocol to overstate its backing and fail to deliver promised returns.

### Finding Description
In `NodeDelegator.stake32Eth()`, the counter is unconditionally incremented:

```solidity
stakedButUnverifiedNativeETH += 32 ether;
``` [1](#0-0) 

The sole decrement path is `verifyWithdrawalCredentials()`:

```solidity
stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));
``` [2](#0-1) 

If the validator's withdrawal credentials do not point to the EigenPod, EigenLayer will reject the credential proof, making `verifyWithdrawalCredentials()` uncallable for that validator. The validator will eventually exit the beacon chain, but `stakedButUnverifiedNativeETH` is never corrected. There is no admin function, no "alienation" path, and no checkpoint-based reconciliation that can decrement this counter for an unverifiable validator.

`getEffectivePodShares()` adds this stale counter to the live `withdrawableShare`:

```solidity
return stakedButUnverifiedNativeETH + withdrawableShare;
``` [3](#0-2) 

`getETHDistributionData()` in `LRTDepositPool` aggregates this across all NDCs:

```solidity
ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
``` [4](#0-3) 

`getTotalAssetDeposits()` calls `getETHDistributionData()`, and `LRTOracle._updateRsETHPrice()` calls `_getTotalEthInProtocol()` which calls `getTotalAssetDeposits()` for every supported asset:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [5](#0-4) 

The inflated `totalETHInProtocol` is then used to compute `rsETHPrice`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [6](#0-5) 

Additionally, if the validator exits with correct credentials (ETH lands in the EigenPod), the 32 ETH is double-counted: once in `stakedButUnverifiedNativeETH` and again in `withdrawableShare` returned by `NodeDelegatorHelper.getWithdrawableShare()`. [7](#0-6) 

### Impact Explanation
The stale counter permanently overstates the protocol's ETH backing. The inflated rsETH price means new depositors receive fewer rsETH tokens per ETH than the true exchange rate warrants. Existing holders appear to hold more value than the protocol actually backs. When redemptions are processed, the protocol cannot deliver the promised asset amounts to all rsETH holders — a classic insolvency pattern. The magnitude is 32 ETH per unverifiable validator, which scales with the number of such validators.

**Impact: Low — Contract fails to deliver promised returns, but doesn't immediately lose value** (escalates toward Critical insolvency as the number of affected validators grows).

### Likelihood Explanation
Low. The trigger requires an LRT Operator to call `stake32Eth()` with incorrect withdrawal credentials (a mistake, not a compromise), followed by the validator exiting the beacon chain before the error is caught. The `stake32EthValidated()` variant checks the deposit root but not the withdrawal credentials, so incorrect credentials can pass the on-chain check. Once the validator exits, the counter is permanently stuck. No privileged recovery path exists.

### Recommendation
1. Add an admin-callable function (e.g., `decreaseStakedButUnverifiedNativeETH(uint256 amount)`) restricted to `onlyLRTAdmin` or `onlyLRTManager` to allow manual correction when a validator is confirmed to have exited without verification.
2. Alternatively, integrate with EigenPod's checkpoint mechanism: after a checkpoint is finalized, reconcile `stakedButUnverifiedNativeETH` against the actual number of active validators proven to EigenLayer, rather than relying solely on the increment/decrement pair.
3. Consider emitting an event and providing a view function that exposes the current unverified validator count so off-chain monitoring can detect drift.

### Proof of Concept
1. Operator calls `stake32Eth(pubkey, signature, depositDataRoot)` with withdrawal credentials that do not point to the NDC's EigenPod. `stakedButUnverifiedNativeETH += 32 ether`.
2. The validator activates on the beacon chain and later exits (voluntarily or via slashing). ETH is sent to the incorrect withdrawal address, not the EigenPod.
3. The operator attempts `verifyWithdrawalCredentials()` — EigenLayer rejects the proof because the on-chain withdrawal credentials do not match the EigenPod address. The call reverts.
4. `stakedButUnverifiedNativeETH` remains permanently inflated by 32 ETH. No other code path can decrement it.
5. Every subsequent call to `updateRSETHPrice()` computes `totalETHInProtocol` with the phantom 32 ETH included, inflating `rsETHPrice`.
6. New depositors receive fewer rsETH per ETH. When they later redeem, the protocol cannot cover all outstanding rsETH at the promised rate.

### Citations

**File:** contracts/NodeDelegator.sol (L166-166)
```text
        stakedButUnverifiedNativeETH += 32 ether;
```

**File:** contracts/NodeDelegator.sol (L240-240)
```text
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));
```

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/LRTDepositPool.sol (L487-487)
```text
            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
