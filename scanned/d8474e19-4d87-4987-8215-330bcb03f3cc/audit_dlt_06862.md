# [H] Governance veto can be bypassed

## Summary
Severity: High
Chain: Smart contract
Component: 2021-11-vader
Published: 2021-11-15
Source: https://github.com/code-423n4/2021-11-vader-findings/issues/186
Type: code-finding

## Details
# Handle

gzeon


# Vulnerability details

## Impact
Since `veto` ensure none of the actions in proposal being vetoed point to the contract (GovernorAlpha.sol:L562), a malicious proposal can be designed to have an action that point to governance and therefore effectively cannot be vetoed.

## Proof of Concept
For any attacker who want to launch a governance attack using a malicious proposal, they simply need to add an action that point to governance that does nothing (or anything). 

## Recommended Mitigation Steps
Some other design can be proposal are vetoable whenever the differential is less than x%, even if it involves governance change, s.t. council can veto most malicious proposal while it is still possible to change council given high enough vote differential.
