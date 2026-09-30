# [M] Vulnerable GovernorVotesQuorumFraction ver-sion used

## Summary
Severity: Medium
Contest weight: 0.3982
Dataset id: 19802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol uses an OZ version of contracts that contain a known vulnerability in government contracts.
UXDGovernor contract inherits from GovernorVotesQuorumFraction:
```solidity
contract UXDGovernor is
    ReentrancyGuard,
    Governor,
    GovernorVotes,
    GovernorVotesQuorumFraction,
    GovernorTimelockControl,
    GovernorCountingSimple,
    GovernorSettings
```
An OZ security recommendation has revealed a known vulnerability in this contract:
https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-xrc4-737v-9q75
It was patched in version 4.7.2, but this protocol uses an older version:
"@openzeppelin/contracts": "^4.6.0"
The potential impact is described in the OZ advisory. This issue was assigned with a severity of High from OZ, so I am sticking with it in this submission.

## Recommendation
Update the OZ version of contracts to version >=4.7.2 or at least follow the workarounds of OZ if not possible otherwise.
