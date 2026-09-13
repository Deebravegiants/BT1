# [M] Iterations over slashes

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Every user should iterate over each slash (but only once) and process them in order to determine whether this slash impacted his delegations or not. 

However, the check is done during almost every action that the user does because it updates the current state of the user's balance. The downside of this method is that if there are a lot of slashes in the system, every user would be forced to iterate over all of them even if the user is only trading tokens and only calls `transfer` function. 

If the number of slashes is huge, checking them all in one function would impossible due to the block gas limit. It's possible to call the checking function separately and process slashes in batches. So this attack should not result in system halt and can be mitigated with manual intervention.

Also, there are two separate pipelines for iterating over slashes. One pipeline is for iterating over months to determine amount of slashed tokens in separate delegations. This one can potentially hit gas limit in many-many years. The other one is for modifying aggregated delegation values.

#### Recommendation

Try to avoid all the unnecessary iterations over a potentially unlimited number of items. Additionally, it's possible to optimize some calculations:

1. When slashing signals are processed, all of them always have the same `holder`. There's no reason for having an array of signals with the same holder (always with predefined length and values will most likely be zero). It seems possible to remove signals functionality and just aggregate the changes for the `Punisher`.
2. Try merge two pipelines into one.
