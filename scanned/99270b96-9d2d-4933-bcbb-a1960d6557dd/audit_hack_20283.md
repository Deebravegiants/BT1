# [H] 5.2.11processEpoch()needs to be called regularly

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:**

- PublicVault.sol#L247
- PublicVault.sol#L320
**Description:** If theprocessEpoch()endpoint does not get called regularly (especially close to the epoch bound-
aries), the updatedcurrentEpochwould lag behind the actual expected value and this will introduce arithmetic
errors in formulas regarding epochs and timestamps.
**Recommendation:** Thus public vaults need to create a mechanism so that theprocessEpoch()gets called
regularly maybe using relayers or off-chain bots.
Also if there are any outstanding withdraw reserves, the vault needs to be topped up with assets (and/or the
current withdraw proxy) so that the full amount of withdraw reserves can be transferred to the withdraw proxy from
the epoch before usingtransferWithdrawReserve, otherwise, the processing of epoch would be halted. And if
this halt continues more than one epoch length, the inaccuracy in the epoch number will be introduced in the
system.
Another mechanism that can be introduced into the system is of incrementing the current epoch not just by one but
by an amount depending on the amount of time passed since the last call to theprocessEpoch()or the timestamp
of the current epoch.
**Astaria:** Acknowledged.
**Spearbit:** Acknowledged.
