# [M] Proposals overwrite

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-08-olympus
Published: 2022-09-01
Source: https://github.com/code-423n4/2022-08-olympus-findings/issues/201
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-08-olympus/blob/b5e139d732eb4c07102f149fb9426d356af617aa/src/policies/Governance.sol#L167
https://github.com/code-423n4/2022-08-olympus/blob/b5e139d732eb4c07102f149fb9426d356af617aa/src/policies/Governance.sol#L66


# Vulnerability details

## Impact
It is possible to overwrite proposals in certain circumstances. The method `Governance.submitProposal` doesn't check if the `proposalId` (stored in a different contract) exists already as a valid proposal in `getProposalMetadata`.

## Proof of Concept

If the project update the kernel module "`INSTR`" and reconfigure proposals and call `INSTR.store(instructions_);`, the counter may return a `proposalId` of an existing proposal and overwrite an existing previous one.

This is due to the fact that the proposals are saved in a mapping of a contract that is not related to the one that returns the counters, and furthermore, they do not check that the record already exists.

```javascript
        uint256 proposalId = INSTR.store(instructions_);
        getProposalMetadata[proposalId] = ProposalMetadata(
            title_,
            msg.sender,
            block.timestamp,
            proposalURI_
        );
```

## Recommended Mitigation Steps
- Store the proposal metadata in the same `INSTR` contract or ensure that the proposal doesn't exists.
