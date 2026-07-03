Audit Report

## Title
Permissionless `verifyCheckpointProofs` + `updateRSETHPrice` Enables Theft of Beacon-Chain Yield — (`contracts/LRTOracle.sol`, `contracts/NodeDelegator.sol`, `contracts/external/eigenlayer/interfaces/IEigenPod.sol`)

## Summary
After an operator calls `NodeDelegator.startCheckpoint()`, an attacker can deposit ETH at the stale pre-yield rsETH price, then permissionlessly finalize the checkpoint via `IEigenPod.verifyCheckpointProofs()` and trigger `LRTOracle.updateRSETHPrice()`. Because the attacker's rsETH was minted at the old price before yield `Y` was credited, they capture a portion of `Y` that should accrue only to pre-existing holders. The `pricePercentageLimit` guard is bypassable when set to zero or when yield is small relative to TVL.

## Finding Description
**Root cause:** Three independently permissionless operations compose into an exploitable sequence with no atomicity or ordering guarantee between them.

**Code path:**

1. `NodeDelegator.startCheckpoint()` (L259–261) is `onlyLRTOperator` and opens a checkpoint. At this point, accumulated beacon-chain yield `Y` is not yet reflected in EigenLayer shares because `recordBeaconChainETHBalanceUpdate` is only called on finalization.

2. `LRTDepositPool.depositETH()` (L76–93) is public. It calls `getRsETHAmountToMint` (L519–520), which divides by `lrtOracle.rsETHPrice()` — the **last stored** price, which does not include `Y`. The attacker receives `D / P_old` rsETH for `D` ETH.

3. `IEigenPod.verifyCheckpointProofs()` (L186–190) carries **no access control** — the NatSpec explicitly states *"Anyone can call this method."* Calling it with valid beacon-chain proofs (publicly derivable from beacon state) finalizes the checkpoint and credits `Y` ETH of new shares to the NDC via `recordBeaconChainETHBalanceUpdate`.

4. `LRTOracle.updateRSETHPrice()` (L87–89) is public (`whenNotPaused` only). It calls `_getTotalEthInProtocol()` → `getTotalAssetDeposits(ETH)` → `getETHDistributionData()` → `getEffectivePodShares()` (L556–561) → `NodeDelegatorHelper.getWithdrawableShare()` → `DelegationManager.getWithdrawableShares()`, which now reflects the newly credited `Y`. The new price is `(N + D + Y − fee) / (S + D/P_old)`, which exceeds `P_old`, making the attacker's rsETH worth more than `D`.

**Why `pricePercentageLimit` is insufficient:**
- At L256–257: `bool isPriceIncreaseOffLimit = pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice)`. If `pricePercentageLimit == 0` (the default after deployment until explicitly set), the entire guard is skipped.
- Even when non-zero, routine staking yield (a few days of rewards) produces a price increase well within any reasonable limit (e.g., 1%), so the attack succeeds fully.

## Impact Explanation
**High — Theft of unclaimed yield.** Pre-existing rsETH holders earned yield `Y` through their prior stake. The attacker dilutes this yield: a fraction of `Y` proportional to `(D/P_old) / (S + D/P_old)` accrues to the attacker's rsETH rather than to existing holders. The attacker can immediately redeem at the new price for a risk-free profit. This matches the allowed impact class *"Theft of unclaimed yield."*

## Likelihood Explanation
**Medium.** The operator must call `startCheckpoint()` first (routine operational step). The window between `startCheckpoint()` and checkpoint finalization can be hours to days. Both `verifyCheckpointProofs` and `updateRSETHPrice` are permissionless. The attacker only needs to watch for `CheckpointCreated` events on-chain and generate beacon-chain balance proofs from public beacon state data (standard EigenLayer tooling exists for this). The attack is repeatable every checkpoint cycle and scales with accumulated yield.

## Recommendation
1. **Restrict `updateRSETHPrice`** to operators/managers, or add a cooldown/lock that prevents price updates while a checkpoint is open (between `startCheckpoint` and finalization).
2. **Alternatively**, snapshot the rsETH total supply at `startCheckpoint()` time and use that supply for yield distribution, so deposits made after the checkpoint opens do not benefit from yield earned before their entry.
3. **Enforce a non-zero `pricePercentageLimit`** as a required invariant (revert in `initialize` or `reinitialize` if it is zero), and document it as a mandatory configuration parameter.
4. Consider pausing deposits in `LRTDepositPool` for the duration of an open checkpoint, or emit a `CheckpointStarted` event and enforce a deposit pause via the existing `PAUSER_ROLE`.

## Proof of Concept
```solidity
// Fork test (Holesky or mainnet fork)
// Preconditions:
//   - NDC has ACTIVE validators with accumulated yield Y = 1 ETH in pod balance
//   - rsETH supply S = 1000 ether, rsETHPrice P_old = 1.05 ether, TVL N = 1050 ether
//   - pricePercentageLimit = 0 (default) OR Y/N < limit

// Step 1: Operator starts checkpoint (normal operation)
vm.prank(operator);
nodeDelegator.startCheckpoint(false);
// rsETHPrice is still 1.05 ether; Y not yet in EigenLayer shares

// Step 2: Attacker deposits 10 ETH at stale price
vm.prank(attacker);
lrtDepositPool.depositETH{value: 10 ether}(0, "");
// Attacker receives 10e18 / 1.05e18 ≈ 9.523 rsETH at old price

// Step 3: Attacker finalizes checkpoint (permissionless — no access control)
// Proofs are derived from public beacon chain state
eigenPod.verifyCheckpointProofs(balanceContainerProof, proofs);
// EigenLayer credits Y = 1 ETH of new shares to NDC via recordBeaconChainETHBalanceUpdate

// Step 4: Attacker triggers price update (permissionless)
lrtOracle.updateRSETHPrice();
// newTVL = 1050 + 10 + 1 = 1061 ETH (minus fee)
// newSupply = 1000 + 9.523 = 1009.523 rsETH
// newPrice ≈ 1061 / 1009.523 ≈ 1.0510 ether

// Step 5: Assert attacker profit
uint256 attackerRsETH = rsETH.balanceOf(attacker); // ≈ 9.523 rsETH
uint256 attackerValue = attackerRsETH * lrtOracle.rsETHPrice() / 1e18; // ≈ 10.009 ETH
assertGt(attackerValue, 10 ether); // Attacker gained ~0.009 ETH of yield
// Pre-existing 1000 rsETH holders lost a proportional share of the 1 ETH yield
```