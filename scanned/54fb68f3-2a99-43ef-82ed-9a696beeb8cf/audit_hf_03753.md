# [H] The renewal grace period gives users insur-

## Summary
Severity: High
Contest weight: 0.2988
Dataset id: 19912
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a protection position is renewed, the contract checks that the expired timestamp is within the grace period of the current timestamp. The issue is that when it is renewed, it starts insurance at block.timestamp rather than the expiration of the previous protection. The result is that the grace period is effectively free insurance for the user. /ProtectionPoolHelper.sol#L390-L397 When checking if a position can be renewed it checks the expiration of the previous protection to confirm that it is being renewed within the grace period. ol/ProtectionPool.sol#L181-L194 After checking if the protection can be removed it starts the insurance at block.timestamp. The result is that the grace period doesn't collect any premium for it's duration. To abuse this the user would keep renewing at the end of the grace period for the shortest amount of time so that they would get the most amount of insurance for free. One might argue that the buyer didn't have insurance during this time but protection can be renewed at any time during the grace period and late payments are very easy to see coming (i.e. if the payment is due in 30 days and it's currently day 29). The result is that even though technically there isn't insurance the user is still basically insured because they would always be able to renew before a default. Renewal grace period can be abused to get free insurance.

## Recommendation
When renewing protection, the protection should renew from the end of the expired protection not block.timestamp.
