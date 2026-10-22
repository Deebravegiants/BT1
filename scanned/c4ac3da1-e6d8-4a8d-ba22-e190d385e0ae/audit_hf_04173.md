# [M] M-02 | Predictable MagicLP Salt

## Summary
Severity: Medium
Contest weight: 0.0979
Dataset id: 20854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The salt used to deploy the new MagicLP contract in the factory is based upon replicable values that any malicious user may pass in. This way a malicious actor may observe two transactions in the mempool and intentionally get their transaction ordered between them. Transaction 1: Create pool at address A Transaction 2: Send additional funds to pool at address A The attacker may create the exact same pool at address A and end up with the funds in their pool. Currently there is no high impact risk as the owner of the clone does not have any special privileges, but this may be unexpected for the user creating the pool.

## Recommendation
Consider including the msg.sender in the salt for pool creation.
