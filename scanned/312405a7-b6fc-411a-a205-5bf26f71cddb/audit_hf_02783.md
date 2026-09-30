# [C] DarkPoolAssetManager can be drained by looping over join(), joinSplit() or swap() with only some initial amount

## Summary
Severity: Critical
Contest weight: 0.0980
Dataset id: 15186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DarkPoolAssetManager::join(), DarkPoolAssetManager::joinSplit() and DarkPoolAssetManager::swap() don't check if the 2 notes are the same. Thus, using only 1 note, it's possible to double the amount of funds available. When used in a loop, this enables draining the whole asset manager. Here is the poc for join() and joinSplit and here for swap().

## Recommendation
Check if the input notes are the same.
