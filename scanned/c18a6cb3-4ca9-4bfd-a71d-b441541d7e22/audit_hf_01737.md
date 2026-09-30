# [H] MJR-1 Public access to all functions

## Summary
Severity: High
Contest weight: 0.0080
Dataset id: 9508
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of missing access control on every external function of the Controller contract. Because each function is declared public without any modifier, any external account can invoke them. The root cause is that the developer did not restrict privileged operations such as setting parameters, pausing the system, or moving assets. An attacker can call these functions directly, for example by invoking the function that changes the address of a critical component or that triggers a withdrawal, thereby altering protocol state, redirecting funds, or disabling safety mechanisms. This can happen at any time after deployment, as there is no role check; the condition is simply that the caller is an EOA or contract. Users of the protocol are affected because the controller may be manipulated to send tokens to an attacker, freeze deposits, or change fee structures, leading to loss of funds or denial of service. The issue was discovered during a manual source‑code audit where the auditor observed that no access modifiers such as onlyOwner, onlyAdmin, or role‑based checks were present on any function. The problem can be subtle because the functions compile and appear to work correctly for legitimate callers, so a casual test may not reveal the over‑exposure. The appropriate remediation is to introduce proper access control, for example by adding OpenZeppelin's Ownable or AccessControl modifiers to restrict privileged functions to authorized accounts, and to review each function to ensure that only intended callers can execute it. In generic terms this is an “unrestricted public function” bug, a class of access‑control flaw that violates the principle that only trusted actors may perform administrative actions. From a user’s perspective the symptom may be that a transaction they did not initiate appears to have changed protocol parameters, that their balance suddenly drops to zero, or that a withdrawal they expected never arrives because the controller has been hijacked. The mismatch between the expected behavior (only the protocol owner can change settings) and the actual behavior (anyone can) breaks the accounting assumptions of the system and can lead to funds disappearing or the protocol becoming unusable.

## Recommendation
We recommend adding access modificators.
