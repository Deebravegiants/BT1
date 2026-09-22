# [M] 5.3.3 LlamaPolicy.hasRoledoesn't check if a policyholder holds a token

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LlamaPolicy.sol#L
**Description:** Incorrect usage of therevokePolicyfunction can result in a case, where the token of a policyholder
is already burned but still holds a role.
ThehasRolefunction doesn't check if in addition to the role thepolicyholderstill holds the token to be active.
Therolecould still be used in the Llama system.
**Recommendation:** Addif (balanceOf(policyholder) == 0) return falseto thehasRolefunction.
**Llama:** Resolved by commit ad0391 and PR 294.
**Spearbit:** Resolved.
