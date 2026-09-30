# [M] 5.3.16 Lack of vetoer can lead to 51% attack

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** VeloGovernor.sol, EpochGovernor.sol
**Description:** The veto power is important functionality in a governance system in order to protect from malicious
proposals. However there is lack of vetoer inVeloGovernor, this might lead to Velodrome losing their veto power
unintentionally and open to 51% attack.
With 51% attack a malicous actor can change the governor inVotercontract or by pass the tokens whitelist adding
new gauge with malicious token.
References

- dialectic.ch/editorial/nouns-governance-attack-2
- code4rena.com/reports/2022-09-nouns-builder/#m-11-loss-of-veto-power-can-lead-to-51-attack
**Recommendation:** Is recommended to add vetoer with two step validation and add the function to execute a veto.
Example of veto function, should adapt the code to use it:
function veto(bytes32 _proposalId) external {
// Ensure the caller is the vetoer
require(msg.sender == vetoer, "Only vetoer");
ProposalState status = state(proposalId);
// Ensure the proposal has not been executed
require(
status != ProposalState.Canceled && status != ProposalState.Expired && status !=
,! ProposalState.Executed,
"Proposal not active"
);
// Get the pointer to the proposal
Proposal storage proposal = proposals[_proposalId];
// Update the proposal as vetoed
proposal.vetoed = true;
emit ProposalVetoed(_proposalId);
}

**Velodrome:** Acknowledged, given the ability of this to severely disrupt normal operation of the protocol. I think the
simplest way to implement this would be to use the _cancel function provided in Governor. We will also add the
ability to set/change a vetoer, which will most likely be set to emergencyCouncil (will ask for feedback around this).
Are there any recommendations regarding parameters that should be set? e.g. the appropriate quorum fraction?
**Spearbit:** Additional considerations, especially during migration from V1 to V2, there should be a time in which
it will be very cheap to attack the Governor without a vetoer, the first attack could be as simple as raising the
quorum (which may force the V1 price to raise as it becomes more urgent to migrate it for V2) This may be used
for example to enable new tokens which are malicious/privileged with the goal of obtaining emissions from V2 in
perpetuity and keeping enough of a headstart to make it impossible for others to catch up Set of attacks:

- Whitelist privileged pair (to steal emissions)
- Raise quorum to make it harder / impossible to catchup
- Set governor to an EOA / Hijack it


- Create a managed lock and refuse to create it for others
**Velodrome:** Fixed in commit 64fe60.
**Spearbit:** Verified.
