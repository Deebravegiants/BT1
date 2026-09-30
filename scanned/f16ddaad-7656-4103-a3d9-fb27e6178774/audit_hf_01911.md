# [M] StrategyExecutor::disableStrategy() disables the wrong strategy

## Summary
Severity: Medium
Contest weight: 0.0819
Dataset id: 10504
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
StrategyExecutor::disableStrategy() removes a strategy from the enabled array by
moving the last element to the to be deleted element and popping. However, the check to
move the element is incorrect, if (enabled.length > 1) enabled[i] =
enabled[enabled.length - 1];. This will pop the last strategy incorrectly.
Additionally, the id to disable could be sent as an argument to save gas on the lookup and
the loop can break after finding the index.

## Recommendation
The element must be copied when it is not the last one (if it is the last one, it should just be
popped). Thus, the correct check is
if (i != enabled.length - 1) enabled[i] = enabled[enabled.length - 1];.
