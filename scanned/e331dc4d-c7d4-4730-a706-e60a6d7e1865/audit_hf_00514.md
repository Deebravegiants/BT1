# [M] M-05 | Gas Griefing Of Epoch Creation

## Summary
Severity: Medium
Contest weight: 0.0999
Dataset id: 1972
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a new epoch is created, block.timestamp is used as the salt for generating two virtual tokens. In _createVirtualToken, a loop probes for an available salt if a collision occurs. However, the salt increments by 1 on each iteration, making it highly predictable and susceptible to front-running. An attacker can exploit this predictability to deliberately create collisions. During testing, each iteration of the loop was found to cost approximately 600k gas, making it feasible for an attacker to force the epoch creation process to fail due to an Out-of-Gas error.

## Recommendation
Consider using a less predictable and more robust mechanism for generating the salt, such as hashing with block variables. Alternatively, consider using CREATE3 which ensure that the address is only dependent on deployer and salt.
