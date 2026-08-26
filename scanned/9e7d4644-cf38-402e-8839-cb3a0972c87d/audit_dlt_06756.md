# [M] active proposal does not expire

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-08-olympus
Published: 2022-08-30
Source: https://github.com/code-423n4/2022-08-olympus-findings/issues/100
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-08-olympus/blob/2a0b515012b4a40076f6eac487f7816aafb8724a/src/policies/Governance.sol#L265-L289


# Vulnerability details

## Impact
Contract `OlympusGovernance` allows controlling protocol through on-chain governing. The issue is that once proposal is active it does not expire, which means that until the new proposal will be selected, anyone can vote on existing one and potentially execute it when it might cause harm to the protocol.

Scenario:
1. New proposal has been submited, endorsed and activated.
2. Users vote, but the quroum is not being achieved.
3. The proposal is active until new one is getting submitted.
4. 6 months elapses and the current active proposal might cause serious harm to the protocol (since it was created long time ago).
5. Malicious actor votes and executes proposal causing harm to the protocol.

## Proof of Concept
`Governance.sol`:
* https://github.com/code-423n4/2022-08-olympus/blob/2a0b515012b4a40076f6eac487f7816aafb8724a/src/policies/Governance.sol#L265-L289

## Tools Used
Manual Review / VSCode

## Recommended Mitigation Steps
It is recommended to add expiration for the active proposal for example 2 weeks. After that time it should be possible to reject proposal and users should be able to reclaim VOTES tokens.
