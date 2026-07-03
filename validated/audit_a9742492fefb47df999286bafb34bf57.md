### Title
EigenLayer AVS Rewards Permanently Unclaimable While NodeDelegator Is Paused - (File: contracts/NodeDelegator.sol)

### Summary
`NodeDelegator.processClaim` is the sole on-chain path for claiming EigenLayer AVS rewards on behalf of the protocol. It carries a `whenNotPaused` guard. When `LRTConfig.pauseAll()` is invoked, every NodeDelegator in the queue is paused, making `processClaim` revert for the entire duration of the pause. Because the NodeDelegator is the registered earner in EigenLayer's `RewardsCoordinator`, no alternative claim path exists; rewards accumulate unclaimed for as long as the pause persists.

### Finding Description

`LRTConfig.pauseAll()` iterates over every NodeDelegator and calls `pause()` on each one: [1](#0-0) 

`NodeDelegator.processClaim` — the only function that calls `IRewardsCoordinator.processClaim` — is gated by both `onlyLRTOperator` and `whenNotPaused`: [2](#0-1) 

EigenLayer's `RewardsCoordinator.processClaim` enforces that only the earner (the NodeDelegator contract itself) or its designated claimer may submit a claim. Because the NodeDelegator never calls `setClaimerFor`, it is the sole eligible caller. With the NodeDelegator paused, that call always reverts, and rewards sit unclaimed in the `RewardsCoordinator` for the full pause window.

The `FeeReceiver.sendFunds()` path (MEV/execution-layer rewards) is unaffected because `receiveFromRewardReceiver` carries no pause guard: [3](#0-2) 

Only EigenLayer AVS rewards routed through `processClaim` are blocked.

### Impact Explanation

Every second the NodeDelegator remains paused, accrued EigenLayer AVS rewards cannot be forwarded to `eigenLayerRewardReceiver`. If the pause is prolonged — whether due to a contested governance decision, an oracle-triggered halt, or an incident response — the protocol and its depositors lose the yield that would otherwise have compounded into the TVL. This maps to **Medium — Temporary freezing of unclaimed yield** (and approaches permanent if the pause is never lifted).

### Likelihood Explanation

`LRTConfig.pauseAll()` is callable by any address holding `PAUSER_ROLE`, which is expected to be a low-threshold multisig. The `LRTOracle` also auto-pauses `LRTDepositPool` and `LRTWithdrawalManager` on price anomalies; a subsequent manual `pauseAll()` call to extend the pause to NodeDelegators is a realistic operational response. Pauses lasting days to weeks are common in DeFi incident responses, making the yield loss material. [4](#0-3) [5](#0-4) 

### Recommendation

Remove `whenNotPaused` from `processClaim`, or add a separate emergency-claim function that bypasses the pause guard. Claiming rewards from an external coordinator does not alter the NodeDelegator's internal state in a way that the pause is designed to protect, so the guard is unnecessarily restrictive. Alternatively, the NodeDelegator should call `IRewardsCoordinator.setClaimerFor` during initialization to designate a separate, always-active claimer address that can act even when the NodeDelegator itself is paused.

### Proof of Concept

1. Protocol accumulates EigenLayer AVS rewards over time; they are claimable by the NodeDelegator from `RewardsCoordinator`.
2. An incident occurs; `PAUSER_ROLE` calls `LRTConfig.pauseAll()`.
3. All NodeDelegators are paused (confirmed by the loop at `LRTConfig.sol:273-282`).
4. Operator attempts `NodeDelegator.processClaim(claim)` → reverts with `Pausable: paused` due to `whenNotPaused` at `NodeDelegator.sol:206`.
5. No alternative path exists to claim rewards on behalf of the NodeDelegator from `RewardsCoordinator`.
6. Rewards remain frozen in `RewardsCoordinator` for the entire pause duration; if the pause is indefinite, the loss is permanent. [2](#0-1)

### Citations

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```

**File:** contracts/NodeDelegator.sol (L202-209)
```text
    function processClaim(IRewardsCoordinator.RewardsMerkleClaim calldata claim)
        external
        nonReentrant
        onlyLRTOperator
        whenNotPaused
    {
        IRewardsCoordinator(lrtConfig.rewardsCoordinator()).processClaim(claim, lrtConfig.eigenLayerRewardReceiver());
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```

**File:** contracts/LRTOracle.sol (L276-282)
```text
            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
