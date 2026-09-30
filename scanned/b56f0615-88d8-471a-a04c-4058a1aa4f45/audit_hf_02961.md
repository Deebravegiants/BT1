# [M] Centralization attack vector is present in setEnabledState

## Summary
Severity: Medium
Contest weight: 0.0823
Dataset id: 16401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setEnabledState method of WrappedElon allows the owner of the contract to disable (or enable) wrapping and unwrapping of tokens. The issue is that a malicious or a compromised owner can decide to act in a bad way towards users and block unwrapping of the tokens, essentially locking them out of their funds. If the ownership is burned then (or private keys are lost) it will be irreversible.

## Recommendation
Potential mitigations here are to use governance or a multi-sig as the contract owner. Even better is to use a Timelock contract that allows users to be notified prior to enabling/disabling wrapping/unwrapping so that they can take action, although this removes the benefit of using the method as a risk mitigation for bridge attacks.
