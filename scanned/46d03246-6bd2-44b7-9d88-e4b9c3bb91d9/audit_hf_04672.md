# [M] Post-proposal vote quorum/threshold checks

## Summary
Severity: Medium
Contest weight: 0.5953
Dataset id: 22420
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pessimistic vote casting approach stores its cutoffs based on the total supply during proposal creation, rather than looking up the current value for each check.

gOHM token holders can delegate their voting rights either to themselves or to an address of their choice. Due to the elasticity in the gOHM supply, and unlike the original implementation of Governor Bravo, the Olympus governance system relies on dynamic thresholds based on the total gOHM supply. This mechanism sets specific thresholds for each proposal, based on the current supply at that time, ensuring that the requirements (in absolute gOHM terms) for proposing and executing proposals scale with the token supply. https://git

The above means that over time, due to dynamic minting and burning, the total supply will be different at different times, whereas the thresholds/quorums checked against are solely the ones set during proposal creation.

DoS of the voting system, preventing proposals from ever passing, under certain circumstances

Consider the case of a bug where there is some sort of runaway death spiral bug or attack in the dymamic burning of gOHM (e.g. opposite of Terra/Luna), and the only fix is to pass a proposal to disable the module(s) causing a problem where everyone is periodically having their tokens burn()-from-ed. At proposal creation there are sufficient votes to pass the threshold, but after the minimum 3-day waiting period, the total supply has been halved, and the original proposer no longer has a sufficient quorum to execute the proposal (or some malicious user decides to cancel it, and there is no user for which isWhitelisted() returns true).

No proposal can fix the issue, since no proposal will have enough votes to pass, by the time it's time to vote. Finally, once the total supply reaches low wei amounts, the treasury can be stolen by any remaining holders, due to loss of precision:
• getProposalThresholdVotes(): min threshold is 1_000, so if supply is <100, don't need any votes to pass anything
• getQuorumVotes(): quorum percent is hard-coded to 20_000 (20%), so if supply drops below 5, quorum is zero
• getHighRiskQuorumVotes(): high percent is hard-coded to 30_000 (30%), so if supply drops below 4, quorum is zero for high risk

The quorum comes from the total supply...
// File: src/external/governance/GovernorBravoDelegate.sol : GovernorBravoDelegate.getHighRiskQuorumVotes()
#1
```solidity
function getQuorumVotes() public view returns (uint256) {
    return (gohm.totalSupply() * quorumPct) / 100_000;
}
...
function getHighRiskQuorumVotes() public view returns (uint256) {
    return (gohm.totalSupply() * highRiskQuorum) / 100_000;
}
```
ain/bophades/src/external/governance/GovernorBravoDelegate.sol#L696-L708

...and is set during propose(), and checked as-is against the eventual vote:
// File: src/external/governance/GovernorBravoDelegate.sol : GovernorBravoDelegate.getVoteOutcome()
#2
```solidity
} else if (
    (proposal.forVotes * 100_000) / (proposal.forVotes + proposal.againstVotes) < approvalThresholdPct ||
    proposal.forVotes < proposal.quorumVotes
) {
    return false;
}
```
ain/bophades/src/external/governance/GovernorBravoDelegate.sol#L804-L810

## Recommendation
Always calculate the quorum and thresholds based on the current gohm.totalSupply() as is done in the OZ implementation, and consider making votes based on the fraction of total supply held, rather than a raw amount, since vote tallies are affected too
