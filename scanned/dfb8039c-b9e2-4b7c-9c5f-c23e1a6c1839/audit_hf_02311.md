# [H] Front-Running of Proposal Tallies

## Summary
Severity: High
Contest weight: 0.6359
Dataset id: 12592
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OneSwap defines a standard work-flow to submit, vote, and execute proposals that enact on the system-wide operations. There are four types of proposals, i.e., _PROPOSAL_TYPE_FUNDS, _PROPOSAL_TYPE_PARAM, _PROPOSAL_TYPE_UPGRADE, and _PROPOSAL_TYPE_TEXT. The _PROPOSAL_TYPE_FUNDS proposal allows for the allocation of certain ones assets to fund a particular project (or effort); the _PROPOSAL_TYPE_PARAM proposal enables dynamic configuration of system-wide protocol fee in BPS; the _PROPOSAL_TYPE_UPGRADE proposal allows for upgrade of the OneSwap DEX engine; the last type, i.e., _PROPOSAL_TYPE_TEXT, is currently a placeholder. The proposal falls in three different phases: submit, vote, and tally. The tally phase will immediately execute the proposal if passed. Our analysis shows that the tally() function counts the user votes and is responsible for execute passed proposals. We notice the criteria of determining whether a proposal is passed is based on the balance sum of users who voted yes. And the balance is measured at the very moment when tally() occurs.
```solidity
// Count the votes, if the result is "Pass", transfer coins to the beneficiary
function tally(uint64 proposalID, uint64 maxEntry) external override {
    Proposal memory proposal = proposals[proposalID];
    require(proposal.deadline != 0, "OneSwapGov: NO_PROPOSAL");
    // solhint-disable-next-line not-rely-on-time
    require(uint(proposal.deadline) <= block.timestamp, "OneSwapGov: DEADLINE_NOT_REACHED");
    require(maxEntry == _MAX_UINT64 || (maxEntry > 0 && msg.sender == IOneSwapToken(ones).owner()), "OneSwapGov: INVALID_MAX_ENTRY");
    address currVoter = lastVoter[proposalID];
    require(currVoter != address(0), "OneSwapGov: NO_LAST_VOTER");
    uint yesCoinsSum = _yesCoins[proposalID];
    uint yesCoinsOld = yesCoinsSum;
    uint noCoinsSum = _noCoins[proposalID];
    uint noCoinsOld = noCoinsSum;
    for (uint64 i = 0; i < maxEntry && currVoter != address(0); i++) {
        Vote memory v = votes[proposalID][currVoter];
        if (v.opinion == _YES)
            yesCoinsSum += IERC20(ones).balanceOf(currVoter);
        if (v.opinion == _NO)
            noCoinsSum += IERC20(ones).balanceOf(currVoter);
        delete votes[proposalID][currVoter];
        currVoter = v.prevVoter;
    }
```
As a result, if a malicious actor chooses to front-run the tally() transaction, with enough voting assets, the actor can largely control the tally() results. And flashloans can readily meet the need of enough voting assets for this front-running attack. The fundamental reason while such attack is possible is due to the way how voting weights are calculated. Without locking up any asset to be committed for the votes, the proposal-based governance system carry less weight in the final results. Moreover, by only counting the voting weights when the tally() operation occurs and the tally() operation may not finish within a single transaction, it unnecessarily provides room for manipulation.

## Recommendation
Develop an effective counter-measure against the manipulation of tally() results.
