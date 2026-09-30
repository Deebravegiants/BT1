# [M] `withdrawFees` does not update checkpoint

## Summary
Severity: Medium
Contest weight: 0.2440
Dataset id: 19192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the fee withdrawal path of the Livepeer protocol where the function that allows a delegator to pull accumulated fees does not trigger a bonding state checkpoint. When a delegator calls withdrawFees, the function is wrapped with the autoClaimEarnings modifier, which correctly claims any pending earnings and updates the delegator’s lastClaimRound and bondedAmount in the BondingManager storage. However, the protocol also maintains a separate BondingVotes contract that records a delegator’s voting power based on checkpointed bonding data. The checkpointing step, normally performed by the autoCheckpoint modifier (or an explicit call to _checkpointBondingState), is never invoked inside withdrawFees. As a result, after a fee withdrawal the delegator’s lastClaimRound and bondedAmount values are refreshed in BondingManager but remain stale in BondingVotes. This discrepancy means that the on‑chain view of voting power and any calculations that rely on the checkpointed state – such as fee distribution, governance voting weight, or reward eligibility – are based on outdated information. An attacker could repeatedly call withdrawFees to claim fees while keeping the bonding checkpoint unchanged, thereby preserving an inflated voting power or manipulating reward calculations. The impact is medium severity because it does not directly steal funds, but it can lead to inaccurate accounting, potential governance manipulation, and unfair fee allocation. The issue manifests only when withdrawFees is executed; any other path that updates bonding state via the autoCheckpoint modifier remains correct. Delegators, protocol governance mechanisms, and any external contracts that query BondingVotes for voting weight are affected. The flaw was uncovered during a Code4rena audit by tracing the call flow of withdrawFees and noticing the absence of a checkpoint call. It is subtle because the primary storage variables appear to be updated, so a quick glance at balances shows no anomaly, while the hidden voting snapshot stays out‑of‑date. To remediate, the withdrawFees function should be protected with the autoCheckpoint modifier (or explicitly invoke _checkpointBondingState) so that the BondingVotes contract records the latest bonding state immediately after fees are withdrawn, ensuring consistency between fee accounting and voting power calculations.

## Proof of Concept
The withdrawFee function has the autoClaimEarnings modifier:

```
    function withdrawFees(address payable _recipient, uint256 _amount) external whenSystemNotPaused currentRoundInitialized autoClaimEarnings(msg.sender) {
```

which calls _autoClaimEarnings:

```
modifier autoClaimEarnings(address _delegator) {
        _autoClaimEarnings(_delegator);
        _;
```

which calls updateDelegatorWithEarnings:

```
function _autoClaimEarnings(address _delegator) internal {
        uint256 currentRound = roundsManager().currentRound();
        uint256 lastClaimRound = delegators[_delegator].lastClaimRound;
        if (lastClaimRound < currentRound) {
            updateDelegatorWithEarnings(_delegator, currentRound, lastClaimRound);
        }
    }
```

During updateDelegatorWithEarnings, both delegator.lastClaimRound and delegator.bondedAmount can be assigned new values.

```
        del.lastClaimRound = _endRound;
        // Rewards are bonded by default
        del.bondedAmount = currentBondedAmount;
```

However, during the lifecycle of all these functions, _checkpointBondingState is never called either directly or through the autoCheckpoint modifier resulting in lastClaimRound & bondedAmount’s values being stale in BondingVotes.sol.

## Recommendation
Add autoCheckpoint modifier to the withdrawFees function.

<https://github.com/livepeer/protocol/pull/623>
