# [M] MapleGlobals, activatePoolManager() has no check that the pool manager is actually a valid pool manager.

## Summary
Severity: Medium
Contest weight: 0.1666
Dataset id: 10240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MapleGlobals, activatePoolManager(), there is no check that the Pool Manager and Pool Delegate are valid, so the governor can mistakenly set malicious addresses as activated. Exploit scenario ● governor was tricked into activating a fake pool manager, which works because it does not validate if the pool delegate of the pool manager is a valid pool delegate nor if the poolManager is a valid poolManager ● a real pool delegate calls acceptPoolDelegate() on a pool manager, but the fakePoolManager frontruns it and calls transferOwnedPoolManager(...) with the toDelegate argument as the pool delegate ● the pool delegate is now the owner of the fake pool in the mapping poolDelegates[delegate_].ownedPoolManager = poolManager_ ● the acceptPoolDelegate transaction to the real pool manager will fail because the pool delegate is already the owner of the fake pool manager (require(poolDelegates[delegate_].ownedPoolManager == address(0), "MG:APM:ALREADY_OWNS"); in activatePoolManager ● the pool delegate does not notice that he is the owner of the fake pool manager instead of the real pool manager and calls deposit cover, which has malicious code, and sends the funds to the attacker

## Recommendation
Check the validity of the Pool Delegate and Pool Manager in activatePoolManager(...).
