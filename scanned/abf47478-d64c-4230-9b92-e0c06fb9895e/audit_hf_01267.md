# [C] UniActionPolicy does not persist usages

## Summary
Severity: Critical
Contest weight: 0.7706
Dataset id: 5861
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UniActionPolicy is an action policy that inspects certain sections of calldata and enforces limits on the inspected values. This policy also allows thresholds to be set and gradually filled over time, so that each call contributes to the total usage across all calls:
```solidity
/**
 * @title UniActionPolicy: Universal Action Policy
 * @dev A policy that allows defining custom rules for actions based on function signatures.
...
 * Also, rules feature usage limits for arguments.
 * For example, you can limit not just max amount for a transfer,
 * but also limit the total amount to be transferred within a permission.
...
 */
```
However, the current implementation does not properly enforce these limits. To see this, notice that the only function that increments the rule.usage.used value is a view function which is not used in a way that persists the change:
```solidity
function checkAction(/* ... */) external returns (uint256) {
    // ...
    for (uint256 i = 0; i < length; i++) {
        if (!config.paramRules.rules[i].check(data)) return VALIDATION_FAILED;
    }
    // ...
}

function check(ParamRule memory rule, bytes calldata data) internal view returns (bool) {
    // ...
    if (rule.isLimited) {
        if (rule.usage.used + uint256(param) > rule.usage.limit) {
            return false;
        }
        rule.usage.used += uint256(param);
    }
    // ...
}
```
As a result, usage amounts will never accumulate as intended. This behavior could allow, for example, more tokens to be withdrawn from an account than was originally intended.

## Recommendation
To ensure usages are persisted across multiple calls, modify the check() function to accept a storage variable instead of memory and remove the view modifier.
