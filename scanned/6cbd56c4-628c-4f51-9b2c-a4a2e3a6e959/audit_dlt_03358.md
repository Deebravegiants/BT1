# [M] Missing event & timelock for critical onlyAdmin functions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-swivel
Published: 2021-10-06
Source: https://github.com/code-423n4/2021-09-swivel-findings/issues/101
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

onlyAdmin functions that change critical contract parameters/addresses/state should emit events and consider adding timelocks so that users and other privileged roles can detect upcoming changes (by offchain monitoring of events) and have the time to react to them.

Privileged functions in all contracts, for e.g. VaultTracker onlyAdmin, have direct financial or trust impact on users who should be given an opportunity to react to them by exiting/engaging without being surprised when changes initiated by such functions are made effective opaquely (without events) and/or immediately (without timelocks).

See similar Medium-severity finding in ConsenSys's Audit of 1inch Liquidity Protocol (https://consensys.net/diligence/audits/2020/12/1inch-liquidity-protocol/#unpredictable-behavior-for-users-due-to-admin-front-running-or-general-bad-timing)

## Proof of Concept

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L36-L59

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L70-L98

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L102-L129

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L132-L138

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L144-L196

https://github.com/Swivel-Finance/gost/blob/5fb7ad62f1f3a962c7bf5348560fe88de0618bae/test/vaulttracker/VaultTracker.sol#L201-L239

and others

## Tools Used
Manual Analysis

## Recommended Mitigation Steps

Add events to all possible flows (some flows emit events in callers) and consider adding timelocks to such onlyAdmin functions.
