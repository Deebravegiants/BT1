# [M] M-02 - Malicious users can set their hooks to contracts that will always revert, causing Claimers to get their tx to claim the user's prizes to be reverted

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-24
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/69
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1318-L1357


# Vulnerability details

# Title
M-02 - Malicious users can set their hooks to contracts that will always revert, causing Claimers to get their tx to claim the user's prizes to be reverted


## Original Issue
[M-02 - Unintended or Malicious Use of Prize Winners' Hooks](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/465)

## Details
The previous implementation claimed the prizes for all the winners in one single transaction, each winner was allowed to set arbitrary hooks that would cause the Vault contract to perform arbitrary calls to the address of the user's hooks.
As the original issue mentions, some consequences of allowing executions to arbitrary addresses are unauthorized side transactions with gas paid unbeknownst to the claimer, reentrant calls, or denial-of-service attacks on claiming transactions.

## Mitigation
The mitigation implements a limit of gas that can be spent on each hook's call, and now the hook's call is made using a try-catch block.

The issue about causing DoS on other users is still present, when using a Claimer to claim a user's prizes in batches, if at least one of the hook's calls reverts, the whole tx claim the user's prizes will be reverted.

```solidity
  function claimPrize(
    ...
  ) external onlyClaimer returns (uint256) {
    ...

    if (hooks.useBeforeClaimPrize) {
      try
        hooks.implementation.beforeClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          _fee,
          _feeRecipient
        )
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/69_
