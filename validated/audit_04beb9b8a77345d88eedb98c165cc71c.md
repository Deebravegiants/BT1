Now I have all the information needed to trace the full call chain. Let me verify the exact lines for the loop and the `updateMaxNodeDelegatorLimit` cap check.

The full call chain is confirmed. Here is the complete analysis:

---

### Title
Unbounded O(2N) External-Call Loop in `getETHDistributionData` Makes `depositETH` Revert Out-of-Gas as NDC Count Grows - (`contracts/LRTDepositPool.sol`)

### Summary
Every call to `depositETH` synchronously traverses the entire `nodeDelegatorQueue` and fires two cross-contract calls per entry. Because `updateMaxNodeDelegatorLimit` imposes no ceiling on the queue size, the gas cost of a single deposit grows without bound and will eventually exceed the block gas limit.

### Finding Description
The call chain is:

```
depositETH
  └─ _beforeDeposit                          (LRTDepositPool.sol:661)
       └─ _checkIfDepositAmountExceedesCurrentLimit  (line 677)
            └─ getTotalAssetDeposits          (line 393)
                 └─ getAssetDistributionData  (line 441 → ETH branch)
                      └─ getETHDistributionData  (lines 484-493)
```

Inside `getETHDistributionData`, for every NDC `i` in `nodeDelegatorQueue`:

```solidity
ethLyingInNDCs += nodeDelegatorQueue[i].balance;                          // BALANCE opcode
ethStakedInEigenLayer   += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();   // external call → EigenLayer
ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(...); // external call → EigenLayer
``` [1](#0-0) 

`getEffectivePodShares` delegates to `NodeDelegatorHelper.getWithdrawableShare`, which calls `delegationManager.getWithdrawableShares` — one EigenLayer round-trip per NDC. [2](#0-1) 

`getAssetUnstaking` calls `delegationManager.getQueuedWithdrawals` and then iterates over every queued withdrawal and every strategy inside it — a nested loop, also one EigenLayer round-trip per NDC. [3](#0-2) 

`updateMaxNodeDelegatorLimit` enforces only a lower bound (`>= nodeDelegatorQueue.length`); there is no upper bound whatsoever:

```solidity
function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
    if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
        revert InvalidMaximumNodeDelegatorLimit();
    }
    maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
    ...
}
``` [4](#0-3) 

The default is 10 (set at initialization), but the admin can raise it to any `uint256` value. [5](#0-4) 

### Impact Explanation
With N NDCs in the queue, every `depositETH` (and `depositAsset`) call executes at minimum **2N external calls** to EigenLayer contracts, each of which performs its own storage reads and computation. At a sufficiently large N (well within `uint256` range, and reachable with a raised limit), the cumulative gas exceeds Ethereum's block gas limit (~30 M gas), causing every deposit to revert with out-of-gas. This permanently blocks new deposits until the queue is manually pruned — a temporary freezing of the deposit path and unbounded gas consumption.

### Likelihood Explanation
The precondition is that the admin raises `maxNodeDelegatorLimit` and populates the queue. This is a legitimate operational action (e.g., scaling to more validators). No malicious intent is required; the protocol simply has no guard preventing the queue from growing to a gas-breaking size. The invariant that "a single deposit must complete within a fixed gas budget" is violated by design.

### Recommendation
1. **Cap `maxNodeDelegatorLimit`** at a safe constant (e.g., 50) enforced in `updateMaxNodeDelegatorLimit`.
2. **Decouple accounting from deposits**: cache `totalAssetDeposits` off-chain or via a keeper and only update it lazily, rather than recomputing it on every deposit.
3. Alternatively, **paginate** `getETHDistributionData` so that the full traversal is never required in a single transaction.

### Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 1. Deploy N mock NodeDelegator contracts that implement
//    getEffectivePodShares() and getAssetUnstaking() with trivial returns.
// 2. Admin calls updateMaxNodeDelegatorLimit(N).
// 3. Admin calls addNodeDelegatorContractToQueue([ndc_1, ..., ndc_N]).
// 4. Any EOA calls depositETH{value: 1 ether}(0, "").
// 5. Measure gas used; assert it grows linearly with N.
// 6. At N ≈ 500–1000 (depending on EigenLayer mock complexity),
//    the call reverts with out-of-gas on a 30 M gas block.

function testUnboundedGas(uint256 N) public {
    // deploy N mock NDCs, register them
    for (uint256 i = 0; i < N; i++) {
        MockNDC ndc = new MockNDC();
        ndcs[i] = address(ndc);
    }
    depositPool.updateMaxNodeDelegatorLimit(N);
    depositPool.addNodeDelegatorContractToQueue(ndcs);

    uint256 gasBefore = gasleft();
    depositPool.depositETH{value: 1 ether}(0, "");
    uint256 gasUsed = gasBefore - gasleft();

    // gasUsed grows linearly with N; at large N it exceeds block limit
    assertGt(gasUsed, N * EXTERNAL_CALL_OVERHEAD);
}
```

### Citations

**File:** contracts/LRTDepositPool.sol (L49-49)
```text
        maxNodeDelegatorLimit = 10;
```

**File:** contracts/LRTDepositPool.sol (L290-297)
```text
    function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
        if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
            revert InvalidMaximumNodeDelegatorLimit();
        }

        maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
        emit MaxNodeDelegatorLimitUpdated(maxNodeDelegatorLimit);
    }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/NodeDelegatorHelper.sol (L52-65)
```text
    function getWithdrawableShare(
        ILRTConfig lrtConfig,
        IStrategy strategy
    )
        internal
        view
        returns (uint256 withdrawableShare)
    {
        IStrategy[] memory strategies = new IStrategy[](1);
        strategies[0] = strategy;

        uint256[] memory withdrawableShares = getWithdrawableShares(lrtConfig, strategies);
        return withdrawableShares[0];
    }
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```
