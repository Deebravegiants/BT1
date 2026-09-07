# [H] `TemporalGovernor` can be bricked by `guardian`

## Summary
Severity: High
Chain: Smart contract
Component: 2023-07-moonwell
Published: 2023-07-31
Source: https://github.com/code-423n4/2023-07-moonwell-findings/issues/314
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L27
https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L188-L198
https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L256


# Vulnerability details

## Description
When a `guardian` pauses `TemporalGovernor` they [lose the ability to pause again](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L283). This can then be reinstated by governance using [`grantGuardiansPause`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L188-L198).

However `grantGuardiansPause` can be called when the contract is still paused. This would break the assertions in [`permissionlessUnpause`]((https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L256)) and [`togglePause`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L289): `assert(!guardianPauseAllowed)`.

Also, `TemporalGovernor` [inherits from OpenZeppelin `Ownable`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L27). There the `owner` has the ability to [`renounceOwnership`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol#L73-L75).

This could cause `TemporalGovernor` to end up in a bad state, since [`revokeGuardian`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L205-L221) call that has special logic for revoking the guardian.

There is the ability to combine these two issues to brick the contract:

1. `guardian` pauses the contract.
2. governance sends an instruction for `grantGuardiansPause` which the `guardian` executes (while still paused). This step disables both `permissionlessUnpause` and `togglePause`. Though the contract is still rescuable through `revokeGuardian`.
3. `guardian` calls `renounceOwnership` from `Ownable`. Which disables any possibility to execute commands on `TemporalGovernor`. Hence no more ability to call `revokeGuardian`.

## Impact
The contract is bricked. Since `permissionlessUnpause` can't be called due to the `assert(!guardianPauseAllowed)`. No cross chain calls an be processed because `executeProposal` is `whenNotPaused` and there is no `guardian` to execute `fastTrackProposalExecution`. Thus the `TemporalGovernor` will be stuck in paused state.

It is also possible for the `guardian` to hold the contract hostage before step 3 (`renounceOwnership`) as they are the only ones who can execute calls on it (through `fastTrackProposalExecution`).

This is scenario relies on governance sending a cross chain `grantGuardiansPause` while the contract is still paused and a malicious `guardian` which together are unlikely. Though the [docs](https://github.com/code-423n4/2023-07-moonwell#overview) mention this as a concern:

> Specific areas of concern include:
> ...
> * TemporalGovernor which is the cross chain governance contract. Specific areas of concern include delays, **the pause guardian**, **putting the contract into a state where it cannot be updated.**

## Proof of Concept
Test in `TemporalGovernorExec.t.sol`:
```solidity
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-moonwell-findings/issues/314_
