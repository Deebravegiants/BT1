# [H] Proposals can be cancelled

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-vader
Published: 2021-04-28
Source: https://github.com/code-423n4/2021-04-vader-findings/issues/227
Type: code-finding

## Details
# Handle

@cmichelio


# Vulnerability details


## Vulnerability Details

Anyone can cancel any proposals by calling `DAO.cancelProposal(id, id)` with `oldProposalID == newProposalID`.
This always passes the minority check as the proposal was approved.

## Impact

An attacker can launch a denial of service attack on the DAO governance and prevent any proposals from being executed.

## Recommended Mitigation Steps

Check `oldProposalID == newProposalID`
