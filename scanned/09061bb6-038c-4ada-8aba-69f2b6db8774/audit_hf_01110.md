# [M] Unbounded schnorrData in opPoke

## Summary
Severity: Medium
Contest weight: 0.1700
Dataset id: 4343
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Invalid optimistic pokes should always be challengeable and it is important that the opChallenge call challenging a previous schnorrData submitted through opPoke does not revert and the gas cost do not exceed the block gas limit. Otherwise, the invalid optimistic poke data will automatically be finalized after the challenge period.  
The opChallenge function must copy the schnorrData to memory and hash it to compare it against the committed Schnorr hash. The schnorrData submitted via opPoke is not bounded in size as its feedIds array length can be arbitrary. A malicious feed can create an optimistic poke with a very large feedIds array that would cost more to challenge than the challenge reward, making it economically unprofitable for keepers to challenge it. In the worst case, challenging it might even exceed the block gas limit making it impossible to challenge even given enough incentive. (Note that opPoke might cost more gas than the opChallenge for large schnorrData as the former hashes schnorrData.feedIds twice, making the block gas limit attack vector potentially impossible to execute. We still recommend restricting the size.)

## Recommendation
Consider restricting the size of schnorrData.feedIds in opPoke. It can already be checked that schnorrData.feedIds.length == bar at this point as all valid Schnorr signatures for the current configuration must have been signed by exactly bar feeds.
