# [C] Emergency processing can be blocked

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The main reason for the emergency processing mechanism is that there is a chance that some token transfers might be blocked. For example, a sender or a receiver is in the USDC blacklist. Emergency processing saves from this problem by not transferring tribute token back to the user (if there is some) and rejecting the proposal.


**code/contracts/Moloch.sol:L407-L411**
```solidity
if (!emergencyProcessing) {
    require(
        proposal.tributeToken.transfer(proposal.proposer, proposal.tributeOffered),
        "failing vote token transfer failed"
    );
```

The problem is that there is still a deposit transfer back to the sponsor and it could be potentially blocked too. If that happens, proposal can't be processed and the LAO is blocked.

#### Recommendation

Implementing pull pattern for all token withdrawals would solve the problem. The alternative solution would be to also keep the deposit tokens in the LAO, but that makes sponsoring the proposal more risky for the sponsor.
