# [M] `NounsDAOV3Proposals.cancel`

## Summary
Severity: Medium
Contest weight: 0.7100
Dataset id: 18991
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function cancel(NounsDAOStorageV3.StorageV3 storage ds, uint256 proposalId) external {
    NounsDAOStorageV3.ProposalState proposalState = stateInternal(ds, proposalId);
    if (
        proposalState == NounsDAOStorageV3.ProposalState.Canceled ||
        proposalState == NounsDAOStorageV3.ProposalState.Defeated ||
        proposalState == NounsDAOStorageV3.ProposalState.Expired ||
        proposalState == NounsDAOStorageV3.ProposalState.Executed ||
        proposalState == NounsDAOStorageV3.ProposalState.Vetoed
    ) {
        revert CantCancelProposalAtFinalState();
    }
```

The Canceled/Executed/Vetoed states are final because they cannot be changed once they are set.

The Defeated state is also a final state because no new votes will be cast (`stateInternal()` may return Defeated only if the `objectionPeriodEndBlock` is passed).

But the Expired state depends on the `GRACE_PERIOD` of the timelock, and `GRACE_PERIOD` may be changed due to upgrades. Once the `GRACE_PERIOD` of the timelock is changed, the state of the proposal may also be changed, so Expired is not the final state.
```solidity
        } else if (block.timestamp >= proposal.eta + getProposalTimelock(ds, proposal).GRACE_PERIOD()) {
            return NounsDAOStorageV3.ProposalState.Expired;
        } else {
            return NounsDAOStorageV3.ProposalState.Queued;
```

Consider the following scenario:

  * Alice submits proposal A to stake 20,000 ETH to a DEFI protocol, and it is successfully passed, but it cannot be executed because there is now only 15,000 ETH in the timelock (consumed by other proposals), and then proposal A expires.
  * The DEFI protocol has been hacked or rug-pulled.
  * Now proposal B is about to be executed to upgrade the timelock and extend `GRACE_PERIOD` (e.g., `GRACE_PERIOD` is extended by 7 days from V1 to V2).
  * Alice wants to cancel Proposal A, but it cannot be canceled because it is in Expired state.
  * Proposal B is executed, causing Proposal A to change from Expired to Queued.
  * The malicious user sends 5000 ETH to the timelock and immediately executes Proposal A to send 20000 ETH to the hacked protocol.

## Recommendation
```solidity
function queue(NounsDAOStorageV3.StorageV3 storage ds, uint256 proposalId) external {
    require(
        stateInternal(ds, proposalId) == NounsDAOStorageV3.ProposalState.Succeeded,
        'NounsDAO::queue: proposal can only be queued if it is succeeded'
    );
    NounsDAOStorageV3.Proposal storage proposal = ds._proposals[proposalId];
    INounsDAOExecutor timelock = getProposalTimelock(ds, proposal);
    uint256 eta = block.timestamp + timelock.delay();
    for (uint256 i = 0; i < proposal.targets.length; i++) {
        queueOrRevertInternal(
            timelock,
            proposal.targets[i],
            proposal.values[i],
            proposal.signatures[i],
            proposal.calldatas[i],
            eta
        );
    }
    proposal.eta = eta;
+   proposal.exp = eta + timelock.GRACE_PERIOD();
...
-   } else if (block.timestamp >= proposal.eta + getProposalTimelock(ds, proposal).GRACE_PERIOD()) {
+   } else if (block.timestamp >= proposal.exp) {
        return NounsDAOStorageV3.ProposalState.Expired;
```

This means that at worst you could directly use...
What the finding also implies, is that if...
We think it would be great to include this issue in the report (at medium severity).
@eladmallel - Changing the `GRACE_PERIOD` is an admin change, which besides misconfiguration is out-of-scope, it is as you described is a rare event. Having a malicious proposal which is passed that got expired is also a rare event. Having a changed `GRACE_PERIOD` that just long enough to make such a malicious proposal become queued is a very rare event, assuming governance is not completely compromised already.

That said, I am ok with this being Medium risk since this is clearly in scope + can be Medium risk with some assumption (tho extreme imo but is subjective), and I would recommend for a fix accordingly. Please let me know if that’s what you want, thanks!

Thank you @gzeon.  
We all agree the odds of the risk materializing is low, we just felt like this was a nice find, and honestly mostly motivated by wanting the warden who found this to have a win :)

It’s not a deal breaker for us if it’s in the report or not, just wanted to express our preference.

Thank you for sharing more of your thinking, it’s helpful!

Low Likelihood + High Severity is generally considered Medium, which is an edge case that fits the medium risk.  
Another thing I would say is that the proposal doesn’t need to be malicious, as I said in the attack scenario where the proposal is normal but expires due to inability to execute for other reasons ( contract balance insufficient, etc.).

@cccz - True, but this is also marginally out-of-scope since an admin action is required, and one may argue it is a misconfiguration if you increase `GRACE_PERIOD` so much that it revive some old passed buggy proposal. 

But given this is marginal and on sponsor’s recommendation, I will upgrade this to Medium.
