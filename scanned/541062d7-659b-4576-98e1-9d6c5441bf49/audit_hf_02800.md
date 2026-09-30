# [H] DarkpoolAssetManager::Split() into 2 equal amounts leads to lost funds

## Summary
Severity: High
Contest weight: 0.0772
Dataset id: 15216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the DarkpoolAssetManager Split function which creates two output notes from a single input note. The implementation does not verify that the two resulting notes are distinct. When the split produces two notes with identical values and identifiers, the nullifier that is consumed to spend the first note is also applied to the second note. Because the nullifier is already marked as spent, the second note cannot be redeemed in any later transaction, effectively locking the assets represented by that note. This situation occurs whenever the caller requests a split that yields equal amounts, for example splitting an even amount into two halves without any additional randomness or differentiation. The root cause is a missing inequality check between the two output notes. An attacker or an unwary user can trigger the condition by selecting an amount that divides evenly, causing half of the intended funds to become inaccessible. From a user perspective the UI may show a successful split and display both notes, but attempts to withdraw or transfer the second note fail silently, leading to confusion such as my balance is lower than expected or the second half is missing. The impact is high because the affected funds are effectively lost unless the contract is upgraded or an admin manually intervenes. The issue was discovered during a manual audit that examined the Split logic and identified the absence of a _noteOut1 != _noteOut2 requirement. The bug is subtle because the function does not revert or emit an error, so the failure is only observable when the second note is later used. The appropriate fix is to add a check that the two output notes are not equal before completing the split, ensuring each note has a unique nullifier and can be spent independently. This class of bug can be described as a nullifier collision or duplicate output vulnerability that breaks the accounting assumptions of one‑to‑one correspondence between notes and spendable rights.

## Recommendation
In DarkpoolAssetManager::Split() add a _noteOut1 != _noteOut2 check.
