# [C] CBU-1 | Malicious Revert Bytes

## Summary
Severity: Critical
Contest weight: 0.2849
Dataset id: 18158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In each callback function the bytes memory reasonBytes returned from the third party callback contract in the event of an error is loaded into memory in the catch case. reasonBytes can be potentially very large and therefore extremely gas intensive when it is copied into memory. Furthermore, the catch block continues to perform computation with reasonBytes, first parsing the error message with ErrorUtils.getRevertMessage and also emitting an event that contains reasonBytes. An attacker may simply implement a callback contract that reverts with an extremely large reasonBytes so that the execution tx would require more gas than the block gas limit. The attacker can then toggle the callback contract to no longer revert when they want their order to be executed successfully, enabling a risk-free trade. In another attack, a trader could observe the keeper’s execution tx in the mempool and front-run it to toggle the callback contract to revert with a large reasonBytes. This would cause the keeper’s execution tx to consume an unforeseen amount of gas and likely run out of gas and fail. The attacker could leverage this in a similar manner to create a risk-free trade opportunity.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/CBU_1.ts

## Recommendation
Do not load the third party callback contract’s error reasonBytes into memory.
