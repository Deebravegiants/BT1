# [M] `activateProposal`

## Summary
Severity: Medium
Contest weight: 0.5412
Dataset id: 16705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no time lock or delay when activating a proposal, the previous one could be replaced immediately. In `vote()` call, a user might want to vote for the previous proposal, but if the `vote()` call and the `activateProposal()` is very close or even in the same block, it is quite possible that the user actually voted for another proposal without much knowledge of. A worse case is some malicious user watching the mempool, and front run a big vote favor/against the `activeProposal`, effectively influence the voting result.

These situations are not what the governance intends to deliver, and might also affect the results of 2 proposals.

## Proof of Concept
`activateProposal()` can take effect right away, replacing the `activeProposal`. And `vote()` does not specify which `proposalId` to vote for, but the `activeProposal` could be different from last second.

src/policies/Governance.sol
```solidity
        function activateProposal(uint256 proposalId_) external {
            ProposalMetadata memory proposal = getProposalMetadata[proposalId_];
    
            if (msg.sender != proposal.submitter) {
                revert NotAuthorizedToActivateProposal();
            }
    
            if (block.timestamp > proposal.submissionTimestamp + ACTIVATION_DEADLINE) {
                revert SubmittedProposalHasExpired();
            }
    
            if (
                (totalEndorsementsForProposal[proposalId_] * 100) <
                VOTES.totalSupply() * ENDORSEMENT_THRESHOLD
            ) {
                revert NotEnoughEndorsementsToActivateProposal();
            }
    
            if (proposalHasBeenActivated[proposalId_] == true) {
                revert ProposalAlreadyActivated();
            }
    
            if (block.timestamp < activeProposal.activationTimestamp + GRACE_PERIOD) {
                revert ActiveProposalNotExpired();
            }
    
            activeProposal = ActivatedProposal(proposalId_, block.timestamp);
    
            proposalHasBeenActivated[proposalId_] = true;
    
            emit ProposalActivated(proposalId_, block.timestamp);
        }
    
        function vote(bool for_) external {
            uint256 userVotes = VOTES.balanceOf(msg.sender);
    
            if (activeProposal.proposalId == 0) {
                revert NoActiveProposalDetected();
            }
    
            if (userVotesForProposal[activeProposal.proposalId][msg.sender] > 0) {
                revert UserAlreadyVoted();
            }
    
            if (for_) {
                yesVotesForProposal[activeProposal.proposalId] += userVotes;
            } else {
                noVotesForProposal[activeProposal.proposalId] += userVotes;
            }
    
            userVotesForProposal[activeProposal.proposalId][msg.sender] = userVotes;
    
            VOTES.transferFrom(msg.sender, address(this), userVotes);
    
            emit WalletVoted(activeProposal.proposalId, msg.sender, for_, userVotes);
        }
```

## Recommendation
Add time delay when activating a proposal, so that users can be aware of that and vote for the current one within the time window.

This is a pretty unique edge case, I can acknowledge as QA.

I actually don’t think its that unique in the case of on chain voting. Imagine a scenario where a user submits a vote with low gas amounts and it is not mined for days later and then the active proposal has changed. I am not sure why the `vote` function wouldn’t take in the intended proposal ID. 

I am going to leave as medium severity as I do think this impacts the intended functionality of the protocol, but am willing to hear more from the sponsor on why they disagree.
