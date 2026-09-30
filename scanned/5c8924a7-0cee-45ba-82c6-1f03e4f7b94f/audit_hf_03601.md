# [H] RROU-1 | Burning bnGMX Could Be Avoided

## Summary
Severity: High
Contest weight: 0.1721
Dataset id: 19580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When unstaking GMX and _shouldReduceBnGmx = true, a proportionate amount of the user's bnGMX wallet balance is burnt. A user can avoid the loss of their bnGMX (any amount beyond what is claimed in _unstakeGmx) by transferring the token to another account they control. After unstaking, the sent bnGMX could be returned. Consequently, a user will have more multiplier points than intended, which will lead to more voting power.

## Proof of Concept
https://github.com/GuardianAudits/GMXV1Updates/blob/aa7755719e42389deae44528d6b2efbbbb84b4b7/test/guardian/Guardian.js#L406

## Recommendation
Consider restricting the transfer of bnGMX for non-handler accounts. Furthermore, clearly document the intended behavior regarding bnGMX slashing upon unstaking GMX.
