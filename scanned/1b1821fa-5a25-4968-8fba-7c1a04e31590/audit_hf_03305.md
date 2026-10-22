# [M] `LinearDistributor.declareReward

## Summary
Severity: Medium
Contest weight: 0.5885
Dataset id: 18142
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the reward distribution contract where the function that declares a new reward computes the incremental vested amount (netVest) by subtracting a stored snapshot (previouslyVested) from the current vested amount reported by an external vesting distributor. The code assumes that the new vesting distributor will always report a vested total that is equal to or greater than the previously recorded snapshot. When an administrator replaces the vestingDistributor address with a different contract that reports a lower total vested amount, the subtraction underflows, causing a revert of the declareReward transaction. This underflow is a classic arithmetic error that stems from a missing validation that the new distributor’s state is monotonic with respect to the stored snapshot. The bug can be triggered simply by calling the admin function setVestingDistributor to point to a new distributor and then invoking declareReward; the transaction will fail, preventing any further reward emission. The impact is that legitimate reward distribution halts, users see no rewards credited, and the protocol may appear to be broken or malicious because funds remain locked in the contract. The condition occurs only after the distributor is changed without also updating the previouslyVested and previouslyVestedTimestamp values, which the contract does not expose for modification outside declareReward. The affected parties are token holders or participants expecting periodic rewards, as well as the protocol operators who cannot resume normal operation after an upgrade. The issue was discovered during a manual audit that examined the arithmetic in declareReward and noted the lack of a guard ensuring currentlyVested >= previouslyVested after a distributor change. It is easy to miss because the subtraction looks innocuous and the contract does not emit any warning before the revert; only a failed transaction reveals the problem. Conceptually, the fix requires resetting the snapshot values (previouslyVested and previouslyVestedTimestamp) when the vestingDistributor is updated, or adding a check that prevents the underflow by refusing to accept a distributor that would cause a negative netVest. This class of bug falls under state‑inconsistent arithmetic underflow and improper handling of external contract upgrades, violating the accounting assumption that vested balances only increase over time. From a user’s perspective the UI would show “reward claim failed” or simply no reward balance change, contrary to the expectation that a new reward should be credited after an upgrade. The failure mode is effectively “funds disappear” in the sense that they remain locked and unrecoverable until the contract state is corrected.

## Proof of Concept
In `LinearDistributor.sol`, there is a [setVestingDistributor()](https://github.com/code-423n4/2023-02-malt/blob/main/contracts/RewardSystem/LinearDistributor.sol#L222-L228) function to update `vestingDistributor`.

And in `declareReward()`, it calculates the `netVest` and `netTime` by subtracting the previous amount and time.

```solidity
File: 2023-02-malt\contracts\RewardSystem\LinearDistributor.sol
112:     uint256 currentlyVested = vestingDistributor.getCurrentlyVested();
113: 
114:     uint256 netVest = currentlyVested - previouslyVested; // @audit revert after change vestingDistributor
115:     uint256 netTime = block.timestamp - previouslyVestedTimestamp;
116: 
```

But there is no guarantee that the vested amount of the new `vestingDistributor` is greater than the previously saved amount after changing the distributor.

Furthermore, there is no option to change `previouslyVested` beside this declareReward() function and it will keep reverting unless the admin change back the distributor.

## Recommendation
I think it would resolve the above problem if we change the previous amounts as well while updating the distributor.

```solidity
function setVestingDistributor(address _vestingDistributor, uint _previouslyVested, uint _previouslyVestedTimestamp)
  external
  onlyRoleMalt(ADMIN_ROLE, "Must have admin privs")
{
  require(_vestingDistributor != address(0), "SetVestDist: No addr(0)");
  vestingDistributor = IVestingDistributor(_vestingDistributor);

  previouslyVested = _previouslyVested;
  previouslyVestedTimestamp = _previouslyVestedTimestamp;
}
```

Setting `previouslyVested` during the `setVestingDistributor` call seems like a sufficient solution to this.
